/**
 * AWS Lambda Handler - Job Scraper Multi-Region
 * Función principal que ejecuta el scraping desde diferentes regiones
 */

const JobScraper = require('../scrapers/jobScraper');
const ProxyRotator = require('../scrapers/proxyRotator');
const WatchlistManager = require('../webhooks/watchlistManager');
const WebhookNotifier = require('../webhooks/webhookNotifier');
const { getSupabaseClient } = require('../supabase/client');

/**
 * Handler principal de Lambda
 */
exports.handler = async (event, context) => {
  const startTime = Date.now();
  console.log('Lambda execution started', { event, region: process.env.AWS_REGION });

  try {
    // Parsear evento
    const payload = typeof event.body === 'string' ? JSON.parse(event.body) : event;
    
    // Configuración
    const config = {
      region: payload.region || process.env.AWS_REGION || 'us-east-1',
      companyId: payload.companyId || null,
      useProxy: payload.useProxy !== false,
      proxyMode: payload.proxyMode || process.env.PROXY_MODE || 'free',
      maxCompanies: payload.maxCompanies || 10,
      hoursThreshold: payload.hoursThreshold || 24
    };

    console.log('Configuration:', config);

    // Inicializar componentes
    const watchlistManager = new WatchlistManager();
    const webhookNotifier = new WebhookNotifier();
    const supabase = getSupabaseClient();

    // Obtener empresas a scrapear
    let companies;
    if (config.companyId) {
      // Scrapear empresa específica
      const { data } = await supabase.getClient()
        .from('watchlist')
        .select('*')
        .eq('id', config.companyId)
        .single();
      companies = data ? [data] : [];
    } else {
      // Scrapear empresas que necesitan actualización
      companies = await watchlistManager.getCompaniesNeedingScrape(config.hoursThreshold);
      companies = companies.slice(0, config.maxCompanies);
    }

    if (companies.length === 0) {
      return buildResponse(200, {
        message: 'No companies need scraping',
        region: config.region,
        duration: Date.now() - startTime
      });
    }

    console.log(`Processing ${companies.length} companies`);

    // Inicializar proxy rotator si es necesario
    let proxyRotator = null;
    if (config.useProxy) {
      proxyRotator = new ProxyRotator({
        mode: config.proxyMode,
        regions: [mapAwsRegionToProxy(config.region)]
      });
      await proxyRotator.initialize();
    }

    // Resultados
    const results = {
      total_companies: companies.length,
      successful: 0,
      failed: 0,
      total_new_jobs: 0,
      companies: []
    };

    // Procesar cada empresa
    for (const company of companies) {
      try {
        console.log(`\n=== Processing ${company.name} ===`);

        // Obtener proxy si está habilitado
        const proxyConfig = proxyRotator ? proxyRotator.getNextProxy() : null;

        // Inicializar scraper
        const scraper = new JobScraper({
          region: config.region,
          useProxy: !!proxyConfig,
          proxyUrl: proxyConfig?.server,
          timeout: 30000
        });

        await scraper.initialize();

        // Obtener jobs existentes para esta empresa
        const { data: existingJobs } = await supabase.getClient()
          .from('jobs')
          .select('link')
          .eq('company_id', company.id);

        const existingLinks = new Set(existingJobs?.map(j => j.link) || []);

        // Scrapear
        const scrapeStart = Date.now();
        const jobs = await scraper.scrapeCompanyJobs(company);
        const scrapeDuration = Date.now() - scrapeStart;

        // Identificar nuevos jobs
        const newJobs = jobs.filter(job => !existingLinks.has(job.link));

        console.log(`Found ${jobs.length} total jobs, ${newJobs.length} new`);

        // Guardar en Supabase
        if (newJobs.length > 0) {
          await scraper.saveJobs(company.id, newJobs);

          // Enviar notificaciones
          await webhookNotifier.notifyNewJobs(company, newJobs);
        }

        // Actualizar última ejecución
        await watchlistManager.updateLastScrape(company.id, jobs.length, true);

        // Log de scraping
        await supabase.logScrape(company.id, config.region, {
          jobs_found: jobs.length,
          new_jobs: newJobs.length,
          success: true,
          duration: scrapeDuration,
          proxy: proxyConfig?.server,
          metadata: {
            scraper_type: company.scraper_type,
            lambda_region: process.env.AWS_REGION
          }
        });

        // Cerrar scraper
        await scraper.close();

        // Agregar a resultados
        results.companies.push({
          id: company.id,
          name: company.name,
          success: true,
          jobs_found: jobs.length,
          new_jobs: newJobs.length,
          duration: scrapeDuration
        });

        results.successful++;
        results.total_new_jobs += newJobs.length;

      } catch (error) {
        console.error(`Error processing ${company.name}:`, error);

        // Actualizar con fallo
        await watchlistManager.updateLastScrape(company.id, 0, false);

        // Log de error
        await supabase.logScrape(company.id, config.region, {
          jobs_found: 0,
          new_jobs: 0,
          success: false,
          error: error.message,
          metadata: {
            scraper_type: company.scraper_type,
            lambda_region: process.env.AWS_REGION
          }
        });

        results.companies.push({
          id: company.id,
          name: company.name,
          success: false,
          error: error.message
        });

        results.failed++;
      }
    }

    const totalDuration = Date.now() - startTime;
    console.log('\n=== Execution Summary ===');
    console.log(`Duration: ${totalDuration}ms`);
    console.log(`Successful: ${results.successful}/${results.total_companies}`);
    console.log(`Total new jobs: ${results.total_new_jobs}`);

    return buildResponse(200, {
      message: 'Scraping completed',
      region: config.region,
      duration: totalDuration,
      results
    });

  } catch (error) {
    console.error('Lambda error:', error);

    return buildResponse(500, {
      error: 'Internal server error',
      message: error.message,
      region: process.env.AWS_REGION,
      duration: Date.now() - startTime
    });
  }
};

/**
 * Construye respuesta HTTP
 */
function buildResponse(statusCode, body) {
  return {
    statusCode,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    },
    body: JSON.stringify(body)
  };
}

/**
 * Mapea región AWS a código de país para proxy
 */
function mapAwsRegionToProxy(awsRegion) {
  const mapping = {
    'us-east-1': 'us',
    'us-west-1': 'us',
    'us-west-2': 'us',
    'eu-west-1': 'gb',
    'eu-west-2': 'gb',
    'eu-central-1': 'de',
    'sa-east-1': 'br',
    'ap-southeast-1': 'sg',
    'ap-northeast-1': 'jp'
  };

  return mapping[awsRegion] || 'us';
}
