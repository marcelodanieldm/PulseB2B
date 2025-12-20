/**
 * Proxy Rotator
 * Gestiona rotación de proxies y regiones para evitar bloqueos
 */

const axios = require('axios');

class ProxyRotator {
  constructor(config = {}) {
    this.config = {
      mode: config.mode || 'free', // 'free', 'smartproxy', 'brightdata'
      regions: config.regions || ['us', 'eu', 'sa'],
      rotationInterval: config.rotationInterval || 5, // minutos
      ...config
    };

    this.proxies = [];
    this.currentProxyIndex = 0;
    this.lastRotation = Date.now();
  }

  /**
   * Inicializa la lista de proxies
   */
  async initialize() {
    if (this.config.mode === 'free') {
      await this.loadFreeProxies();
    } else if (this.config.mode === 'smartproxy') {
      this.setupSmartProxy();
    } else if (this.config.mode === 'brightdata') {
      this.setupBrightData();
    }

    console.log(`✓ Proxy rotator initialized with ${this.proxies.length} proxies`);
  }

  /**
   * Carga proxies gratuitos desde APIs públicas
   */
  async loadFreeProxies() {
    try {
      // API 1: ProxyScrape
      const response1 = await axios.get(
        'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'
      );
      
      const proxies1 = response1.data
        .split('\n')
        .filter(line => line.trim())
        .map(line => ({
          host: line.split(':')[0],
          port: parseInt(line.split(':')[1]),
          type: 'http',
          source: 'proxyscrape'
        }));

      // API 2: Free Proxy List
      const response2 = await axios.get(
        'https://www.proxy-list.download/api/v1/get?type=http'
      );
      
      const proxies2 = response2.data
        .split('\n')
        .filter(line => line.trim())
        .map(line => ({
          host: line.split(':')[0],
          port: parseInt(line.split(':')[1]),
          type: 'http',
          source: 'proxy-list'
        }));

      this.proxies = [...proxies1, ...proxies2].slice(0, 50); // Limitar a 50
      
      // Validar proxies
      await this.validateProxies();

    } catch (error) {
      console.error('Error loading free proxies:', error.message);
      // Fallback: sin proxy
      this.proxies = [{ host: null, port: null, type: 'direct' }];
    }
  }

  /**
   * Configura SmartProxy (servicio de pago)
   */
  setupSmartProxy() {
    const username = process.env.SMARTPROXY_USERNAME;
    const password = process.env.SMARTPROXY_PASSWORD;

    if (!username || !password) {
      console.warn('SmartProxy credentials not found, using free proxies');
      return this.loadFreeProxies();
    }

    // SmartProxy rotating residential proxies
    this.config.regions.forEach(region => {
      this.proxies.push({
        host: 'gate.smartproxy.com',
        port: 7000,
        username: `${username}-country-${region}`,
        password: password,
        type: 'http',
        source: 'smartproxy',
        region: region
      });
    });
  }

  /**
   * Configura BrightData (Luminati)
   */
  setupBrightData() {
    const username = process.env.BRIGHTDATA_USERNAME;
    const password = process.env.BRIGHTDATA_PASSWORD;

    if (!username || !password) {
      console.warn('BrightData credentials not found, using free proxies');
      return this.loadFreeProxies();
    }

    // BrightData residential proxies
    this.config.regions.forEach(region => {
      this.proxies.push({
        host: 'brd.superproxy.io',
        port: 22225,
        username: `${username}-country-${region}`,
        password: password,
        type: 'http',
        source: 'brightdata',
        region: region
      });
    });
  }

  /**
   * Valida que los proxies funcionen
   */
  async validateProxies() {
    const validProxies = [];

    for (const proxy of this.proxies.slice(0, 20)) { // Validar primeros 20
      try {
        const proxyUrl = `http://${proxy.host}:${proxy.port}`;
        const response = await axios.get('https://httpbin.org/ip', {
          proxy: {
            host: proxy.host,
            port: proxy.port
          },
          timeout: 5000
        });

        if (response.status === 200) {
          validProxies.push({
            ...proxy,
            validated: true,
            validatedAt: new Date()
          });
        }
      } catch (error) {
        // Proxy no funciona, skip
        continue;
      }
    }

    this.proxies = validProxies;
    console.log(`✓ Validated ${validProxies.length} working proxies`);
  }

  /**
   * Obtiene el siguiente proxy en rotación
   */
  getNextProxy() {
    // Verificar si necesita rotar
    const minutesSinceRotation = (Date.now() - this.lastRotation) / 1000 / 60;
    
    if (minutesSinceRotation >= this.config.rotationInterval) {
      this.currentProxyIndex = (this.currentProxyIndex + 1) % this.proxies.length;
      this.lastRotation = Date.now();
    }

    const proxy = this.proxies[this.currentProxyIndex];

    if (!proxy || proxy.type === 'direct') {
      return null; // Sin proxy
    }

    // Formato para Playwright
    if (proxy.username && proxy.password) {
      return {
        server: `http://${proxy.host}:${proxy.port}`,
        username: proxy.username,
        password: proxy.password
      };
    }

    return {
      server: `http://${proxy.host}:${proxy.port}`
    };
  }

  /**
   * Obtiene proxy por región específica
   */
  getProxyByRegion(region) {
    const regionProxies = this.proxies.filter(p => p.region === region);
    
    if (regionProxies.length === 0) {
      return this.getNextProxy();
    }

    const proxy = regionProxies[Math.floor(Math.random() * regionProxies.length)];

    if (proxy.username && proxy.password) {
      return {
        server: `http://${proxy.host}:${proxy.port}`,
        username: proxy.username,
        password: proxy.password
      };
    }

    return {
      server: `http://${proxy.host}:${proxy.port}`
    };
  }

  /**
   * Marca un proxy como fallido
   */
  markProxyAsFailed(proxyServer) {
    const index = this.proxies.findIndex(p => 
      `http://${p.host}:${p.port}` === proxyServer
    );

    if (index !== -1) {
      this.proxies.splice(index, 1);
      console.warn(`⚠️ Removed failed proxy: ${proxyServer}`);
    }
  }

  /**
   * Obtiene estadísticas de proxies
   */
  getStats() {
    return {
      total: this.proxies.length,
      current: this.currentProxyIndex,
      mode: this.config.mode,
      regions: [...new Set(this.proxies.map(p => p.region))],
      lastRotation: new Date(this.lastRotation).toISOString()
    };
  }
}

module.exports = ProxyRotator;
