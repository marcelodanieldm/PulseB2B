/**
 * Job Scraper con Playwright Stealth
 * Extrae vacantes de sitios web corporativos con evasión de detección
 */

const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const { createClient } = require('@supabase/supabase-js');

// Configurar Playwright con stealth
chromium.use(StealthPlugin());

// Configurar proxy rotator
const PROXY_PROVIDERS = {
  free: [
    // Free proxy lists - rotar entre diferentes proveedores
    'https://www.proxy-list.download/api/v1/get?type=https',
    'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'
  ],
  // Para producción, usar servicio profesional como:
  // smartproxy: process.env.SMARTPROXY_ENDPOINT,
  // brightdata: process.env.BRIGHTDATA_ENDPOINT,
};

// Rotación de User Agents
const USER_AGENTS = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.1; rv:121.0) Gecko/20100101 Firefox/121.0'
];

class JobScraper {
  constructor(config = {}) {
    this.config = {
      headless: config.headless !== false,
      timeout: config.timeout || 30000,
      region: config.region || 'us-east-1',
      useProxy: config.useProxy || false,
      proxyUrl: config.proxyUrl || null,
      retries: config.retries || 3,
      ...config
    };
    
    this.browser = null;
    this.context = null;
    this.supabase = null;
    
    // Inicializar Supabase si está configurado
    if (process.env.SUPABASE_URL && process.env.SUPABASE_KEY) {
      this.supabase = createClient(
        process.env.SUPABASE_URL,
        process.env.SUPABASE_KEY
      );
    }
  }

  /**
   * Inicializa el navegador con configuración stealth
   */
  async initialize() {
    const launchOptions = {
      headless: this.config.headless,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--disable-gpu',
        '--window-size=1920,1080',
        '--disable-blink-features=AutomationControlled',
      ]
    };

    // Agregar proxy si está configurado
    if (this.config.useProxy && this.config.proxyUrl) {
      launchOptions.proxy = {
        server: this.config.proxyUrl
      };
    }

    this.browser = await chromium.launch(launchOptions);
    
    // Crear contexto con configuración anti-detección
    this.context = await this.browser.newContext({
      userAgent: this.getRandomUserAgent(),
      viewport: { width: 1920, height: 1080 },
      locale: this.getLocaleByRegion(),
      timezoneId: this.getTimezoneByRegion(),
      permissions: [],
      // Simular dispositivo real
      deviceScaleFactor: 1,
      isMobile: false,
      hasTouch: false,
      // Headers adicionales para parecer más humano
      extraHTTPHeaders: {
        'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
      }
    });

    // Evadir detección de webdriver
    await this.context.addInitScript(() => {
      // Ocultar webdriver property
      Object.defineProperty(navigator, 'webdriver', {
        get: () => false
      });

      // Modificar plugins
      Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
      });

      // Chrome runtime
      window.chrome = {
        runtime: {}
      };

      // Permisos
      const originalQuery = window.navigator.permissions.query;
      window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
          Promise.resolve({ state: Notification.permission }) :
          originalQuery(parameters)
      );
    });

    console.log(`✓ Browser initialized for region: ${this.config.region}`);
  }

  /**
   * Obtiene un User Agent aleatorio
   */
  getRandomUserAgent() {
    return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
  }

  /**
   * Obtiene locale según la región
   */
  getLocaleByRegion() {
    const locales = {
      'us-east-1': 'en-US',
      'eu-west-1': 'en-GB',
      'eu-central-1': 'de-DE',
      'sa-east-1': 'pt-BR',
      'default': 'en-US'
    };
    return locales[this.config.region] || locales.default;
  }

  /**
   * Obtiene timezone según la región
   */
  getTimezoneByRegion() {
    const timezones = {
      'us-east-1': 'America/New_York',
      'eu-west-1': 'Europe/London',
      'eu-central-1': 'Europe/Berlin',
      'sa-east-1': 'America/Sao_Paulo',
      'default': 'America/New_York'
    };
    return timezones[this.config.region] || timezones.default;
  }

  /**
   * Simula comportamiento humano
   */
  async simulateHumanBehavior(page) {
    // Movimientos aleatorios del mouse
    await page.mouse.move(
      Math.random() * 1920,
      Math.random() * 1080
    );

    // Scroll aleatorio
    await page.evaluate(() => {
      window.scrollBy(0, Math.random() * 500);
    });

    // Delay aleatorio
    await this.randomDelay(1000, 3000);
  }

  /**
   * Delay aleatorio para parecer humano
   */
  async randomDelay(min, max) {
    const delay = Math.floor(Math.random() * (max - min + 1)) + min;
    await new Promise(resolve => setTimeout(resolve, delay));
  }

  /**
   * Scrape de página de carreras de una empresa
   */
  async scrapeCompanyJobs(company, retryCount = 0) {
    if (!this.context) {
      await this.initialize();
    }

    const page = await this.context.newPage();

    try {
      console.log(`🔍 Scraping jobs for ${company.name} at ${company.careers_url}`);

      // Navegar con timeout
      await page.goto(company.careers_url, {
        waitUntil: 'networkidle',
        timeout: this.config.timeout
      });

      // Simular comportamiento humano
      await this.simulateHumanBehavior(page);

      // Esperar a que cargue el contenido de jobs
      await page.waitForSelector(company.job_selector || 'body', {
        timeout: 10000
      }).catch(() => {
        console.warn(`⚠️ Job selector not found for ${company.name}, using fallback`);
      });

      // Extraer jobs según el sitio
      let jobs = [];

      if (company.scraper_type === 'greenhouse') {
        jobs = await this.scrapeGreenhouse(page, company);
      } else if (company.scraper_type === 'lever') {
        jobs = await this.scrapeLever(page, company);
      } else if (company.scraper_type === 'workday') {
        jobs = await this.scrapeWorkday(page, company);
      } else if (company.scraper_type === 'custom') {
        jobs = await this.scrapeCustom(page, company);
      } else {
        // Scraper genérico
        jobs = await this.scrapeGeneric(page, company);
      }

      console.log(`✓ Found ${jobs.length} jobs for ${company.name}`);

      // Guardar en Supabase si está configurado
      if (this.supabase && jobs.length > 0) {
        await this.saveJobs(company.id, jobs);
      }

      await page.close();
      return jobs;

    } catch (error) {
      console.error(`❌ Error scraping ${company.name}:`, error.message);

      // Retry logic
      if (retryCount < this.config.retries) {
        console.log(`🔄 Retrying (${retryCount + 1}/${this.config.retries})...`);
        await this.randomDelay(2000, 5000);
        return this.scrapeCompanyJobs(company, retryCount + 1);
      }

      await page.close();
      throw error;
    }
  }

  /**
   * Scraper para sitios Greenhouse
   */
  async scrapeGreenhouse(page, company) {
    const jobs = await page.$$eval('.opening', (elements) => {
      return elements.map(el => {
        const title = el.querySelector('a')?.textContent?.trim() || '';
        const link = el.querySelector('a')?.href || '';
        const location = el.querySelector('.location')?.textContent?.trim() || '';
        const department = el.querySelector('.department')?.textContent?.trim() || '';

        return { title, link, location, department };
      });
    });

    return jobs.map(job => ({
      ...job,
      company_id: company.id,
      company_name: company.name,
      scraped_at: new Date().toISOString(),
      source: 'greenhouse'
    }));
  }

  /**
   * Scraper para sitios Lever
   */
  async scrapeLever(page, company) {
    const jobs = await page.$$eval('.posting', (elements) => {
      return elements.map(el => {
        const title = el.querySelector('.posting-title h5')?.textContent?.trim() || '';
        const link = el.querySelector('a')?.href || '';
        const location = el.querySelector('.posting-categories .location')?.textContent?.trim() || '';
        const department = el.querySelector('.posting-categories .department')?.textContent?.trim() || '';

        return { title, link, location, department };
      });
    });

    return jobs.map(job => ({
      ...job,
      company_id: company.id,
      company_name: company.name,
      scraped_at: new Date().toISOString(),
      source: 'lever'
    }));
  }

  /**
   * Scraper para Workday (más complejo)
   */
  async scrapeWorkday(page, company) {
    // Workday requiere interacción con iframes y JavaScript pesado
    await this.randomDelay(3000, 5000);

    const jobs = await page.evaluate(() => {
      const jobElements = document.querySelectorAll('[data-automation-id="compositeContainer"]');
      return Array.from(jobElements).map(el => {
        const title = el.querySelector('[data-automation-id="jobTitle"]')?.textContent?.trim() || '';
        const link = el.querySelector('a')?.href || '';
        const location = el.querySelector('[data-automation-id="location"]')?.textContent?.trim() || '';

        return { title, link, location, department: '' };
      });
    });

    return jobs.map(job => ({
      ...job,
      company_id: company.id,
      company_name: company.name,
      scraped_at: new Date().toISOString(),
      source: 'workday'
    }));
  }

  /**
   * Scraper personalizado usando selectores custom
   */
  async scrapeCustom(page, company) {
    const selector = company.job_selector || '.job-listing';
    const jobs = await page.$$eval(selector, (elements, company) => {
      return elements.map(el => {
        // Intentar múltiples selectores comunes
        const title = 
          el.querySelector('.job-title, .title, h3, h2')?.textContent?.trim() ||
          el.textContent?.trim().split('\n')[0] || '';
        
        const link = el.querySelector('a')?.href || el.closest('a')?.href || '';
        
        const location = 
          el.querySelector('.location, .job-location')?.textContent?.trim() || '';
        
        const department = 
          el.querySelector('.department, .team')?.textContent?.trim() || '';

        return { title, link, location, department };
      });
    }, company);

    return jobs
      .filter(job => job.title && job.link)
      .map(job => ({
        ...job,
        company_id: company.id,
        company_name: company.name,
        scraped_at: new Date().toISOString(),
        source: 'custom'
      }));
  }

  /**
   * Scraper genérico que busca patrones comunes
   */
  async scrapeGeneric(page, company) {
    const jobs = await page.evaluate(() => {
      // Buscar patrones comunes de job listings
      const selectors = [
        '.job', '.position', '.opening', '.career', '.vacancy',
        '[class*="job"]', '[class*="position"]', '[class*="career"]',
        'li a[href*="job"]', 'li a[href*="position"]', 'li a[href*="career"]'
      ];

      let elements = [];
      for (const selector of selectors) {
        elements = document.querySelectorAll(selector);
        if (elements.length > 0) break;
      }

      return Array.from(elements).map(el => {
        const title = el.textContent?.trim() || '';
        const link = el.href || el.querySelector('a')?.href || '';

        return { title, link };
      });
    });

    return jobs
      .filter(job => job.title && job.link)
      .map(job => ({
        ...job,
        company_id: company.id,
        company_name: company.name,
        location: '',
        department: '',
        scraped_at: new Date().toISOString(),
        source: 'generic'
      }));
  }

  /**
   * Guarda jobs en Supabase
   */
  async saveJobs(companyId, jobs) {
    try {
      // Verificar si ya existen (por URL)
      const existingJobs = await this.supabase
        .from('jobs')
        .select('link')
        .eq('company_id', companyId);

      const existingLinks = new Set(
        existingJobs.data?.map(j => j.link) || []
      );

      // Filtrar nuevos jobs
      const newJobs = jobs.filter(job => !existingLinks.has(job.link));

      if (newJobs.length > 0) {
        const { data, error } = await this.supabase
          .from('jobs')
          .insert(newJobs);

        if (error) {
          console.error('Error saving to Supabase:', error);
        } else {
          console.log(`✓ Saved ${newJobs.length} new jobs to Supabase`);
        }
      } else {
        console.log('No new jobs to save');
      }
    } catch (error) {
      console.error('Error in saveJobs:', error);
    }
  }

  /**
   * Cierra el navegador
   */
  async close() {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
      this.context = null;
    }
  }
}

module.exports = JobScraper;
