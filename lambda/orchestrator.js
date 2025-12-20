/**
 * Lambda Orchestrator
 * Coordina la ejecución de scrapers en múltiples regiones
 */

const AWS = require('aws-sdk');
const { getSupabaseClient } = require('../supabase/client');

const lambda = new AWS.Lambda();

exports.handler = async (event, context) => {
  console.log('Orchestrator started');

  try {
    const supabase = getSupabaseClient();
    
    // Obtener empresas por región
    const { data: companies } = await supabase.getClient()
      .from('watchlist')
      .select('id, name, region')
      .eq('active', true);

    // Agrupar por región
    const companiesByRegion = {
      'us': [],
      'eu': [],
      'sa': []
    };

    companies?.forEach(company => {
      const region = company.region || 'us';
      if (companiesByRegion[region]) {
        companiesByRegion[region].push(company.id);
      }
    });

    // Mapping de región a función Lambda
    const regionToFunction = {
      'us': process.env.SCRAPER_FUNCTION_US || 'pulseb2b-scraper-us-east-1',
      'eu': process.env.SCRAPER_FUNCTION_EU || 'pulseb2b-scraper-eu-west-1',
      'sa': process.env.SCRAPER_FUNCTION_SA || 'pulseb2b-scraper-sa-east-1'
    };

    // Invocar Lambda functions por región
    const invocations = [];

    for (const [region, companyIds] of Object.entries(companiesByRegion)) {
      if (companyIds.length === 0) continue;

      const payload = {
        region: region,
        companyIds: companyIds,
        maxCompanies: 10
      };

      const invocation = lambda.invoke({
        FunctionName: regionToFunction[region],
        InvocationType: 'Event', // Asíncrono
        Payload: JSON.stringify(payload)
      }).promise();

      invocations.push(invocation);
      
      console.log(`Invoked ${regionToFunction[region]} for ${companyIds.length} companies`);
    }

    // Esperar a que todas las invocaciones se envíen
    await Promise.all(invocations);

    return {
      statusCode: 200,
      body: JSON.stringify({
        message: 'Orchestration completed',
        regions_invoked: Object.keys(regionToFunction).filter(r => companiesByRegion[r].length > 0),
        total_companies: companies?.length || 0
      })
    };

  } catch (error) {
    console.error('Orchestrator error:', error);

    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'Orchestration failed',
        message: error.message
      })
    };
  }
};
