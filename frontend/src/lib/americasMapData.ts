/**
 * Americas SVG Map Data
 * Simplified SVG paths for countries from Canada to Argentina
 * Coordinates are normalized to a 1000x1500 viewBox
 */

export interface CountryData {
  code: string;
  name: string;
  path: string;
  centroid: [number, number]; // [x, y] for label positioning
  region: 'north_america' | 'central_america' | 'andean_region' | 'southern_cone';
  timezone: number; // Hours from EST
  currency: string;
  color: string; // Default color
}

export const AMERICAS_COUNTRIES: CountryData[] = [
  // NORTH AMERICA
  {
    code: 'CA',
    name: 'Canada',
    path: 'M150,50 L250,40 L350,45 L450,55 L500,80 L520,120 L480,180 L420,200 L350,210 L280,200 L200,180 L150,150 Z',
    centroid: [350, 120],
    region: 'north_america',
    timezone: 0,
    currency: 'CAD',
    color: '#3B82F6'
  },
  {
    code: 'US',
    name: 'United States',
    path: 'M140,220 L220,210 L300,215 L380,220 L460,230 L520,250 L540,300 L530,350 L480,380 L420,390 L350,385 L280,375 L220,360 L180,330 L150,280 Z',
    centroid: [350, 300],
    region: 'north_america',
    timezone: 0,
    currency: 'USD',
    color: '#3B82F6'
  },
  
  // CENTRAL AMERICA
  {
    code: 'MX',
    name: 'Mexico',
    path: 'M180,410 L250,400 L320,405 L380,415 L420,440 L450,480 L430,520 L380,540 L320,550 L260,545 L220,520 L190,480 Z',
    centroid: [320, 470],
    region: 'central_america',
    timezone: -1,
    currency: 'MXN',
    color: '#10B981'
  },
  {
    code: 'GT',
    name: 'Guatemala',
    path: 'M280,560 L310,555 L330,565 L335,580 L325,595 L305,600 L285,590 Z',
    centroid: [310, 575],
    region: 'central_america',
    timezone: -1,
    currency: 'GTQ',
    color: '#10B981'
  },
  {
    code: 'CR',
    name: 'Costa Rica',
    path: 'M320,620 L340,615 L355,625 L360,640 L350,655 L335,660 L320,650 Z',
    centroid: [340, 635],
    region: 'central_america',
    timezone: -1,
    currency: 'CRC',
    color: '#10B981'
  },
  {
    code: 'PA',
    name: 'Panama',
    path: 'M360,665 L385,660 L405,670 L410,685 L395,700 L375,705 L360,695 Z',
    centroid: [385, 680],
    region: 'central_america',
    timezone: 0,
    currency: 'USD',
    color: '#10B981'
  },
  
  // ANDEAN REGION
  {
    code: 'CO',
    name: 'Colombia',
    path: 'M380,710 L420,705 L460,715 L480,740 L490,780 L475,820 L450,840 L420,850 L390,845 L370,820 L360,780 L365,740 Z',
    centroid: [425, 775],
    region: 'andean_region',
    timezone: 0,
    currency: 'COP',
    color: '#F59E0B'
  },
  {
    code: 'VE',
    name: 'Venezuela',
    path: 'M480,720 L530,710 L570,720 L590,750 L585,790 L560,820 L530,830 L500,820 L485,790 Z',
    centroid: [540, 765],
    region: 'andean_region',
    timezone: 1,
    currency: 'VES',
    color: '#F59E0B'
  },
  {
    code: 'EC',
    name: 'Ecuador',
    path: 'M360,860 L390,855 L415,865 L425,890 L415,920 L390,935 L365,930 L355,900 Z',
    centroid: [390, 895],
    region: 'andean_region',
    timezone: 0,
    currency: 'USD',
    color: '#F59E0B'
  },
  {
    code: 'PE',
    name: 'Peru',
    path: 'M380,945 L420,940 L455,955 L475,990 L480,1040 L470,1090 L450,1130 L420,1150 L390,1140 L370,1100 L360,1050 L365,1000 Z',
    centroid: [425, 1045],
    region: 'andean_region',
    timezone: 0,
    currency: 'PEN',
    color: '#F59E0B'
  },
  {
    code: 'BO',
    name: 'Bolivia',
    path: 'M450,1160 L485,1155 L515,1170 L530,1210 L525,1250 L505,1280 L475,1290 L450,1275 L435,1240 L440,1200 Z',
    centroid: [485, 1220],
    region: 'andean_region',
    timezone: 1,
    currency: 'BOB',
    color: '#F59E0B'
  },
  
  // SOUTHERN CONE
  {
    code: 'BR',
    name: 'Brazil',
    path: 'M520,840 L580,850 L640,880 L680,930 L700,990 L710,1060 L705,1130 L690,1190 L660,1240 L620,1270 L570,1285 L520,1280 L490,1250 L475,1200 L470,1140 L480,1080 L495,1020 L510,960 L515,900 Z',
    centroid: [600, 1065],
    region: 'southern_cone',
    timezone: 2,
    currency: 'BRL',
    color: '#EF4444'
  },
  {
    code: 'PY',
    name: 'Paraguay',
    path: 'M520,1290 L555,1285 L580,1300 L590,1330 L580,1360 L555,1375 L530,1370 L515,1340 Z',
    centroid: [555, 1325],
    region: 'southern_cone',
    timezone: 1,
    currency: 'PYG',
    color: '#EF4444'
  },
  {
    code: 'CL',
    name: 'Chile',
    path: 'M420,1160 L445,1155 L455,1190 L460,1240 L465,1300 L468,1360 L470,1420 L465,1480 L455,1520 L440,1530 L425,1525 L415,1490 L410,1440 L408,1380 L407,1320 L410,1260 L415,1200 Z',
    centroid: [438, 1340],
    region: 'southern_cone',
    timezone: 1,
    currency: 'CLP',
    color: '#EF4444'
  },
  {
    code: 'AR',
    name: 'Argentina',
    path: 'M480,1300 L520,1295 L550,1310 L570,1350 L575,1400 L570,1460 L560,1520 L545,1570 L520,1600 L490,1610 L465,1600 L450,1560 L445,1500 L450,1440 L460,1380 L470,1330 Z',
    centroid: [515, 1455],
    region: 'southern_cone',
    timezone: 2,
    currency: 'ARS',
    color: '#EF4444'
  },
  {
    code: 'UY',
    name: 'Uruguay',
    path: 'M590,1380 L615,1375 L635,1390 L640,1415 L630,1440 L610,1450 L590,1440 L585,1410 Z',
    centroid: [615, 1413],
    region: 'southern_cone',
    timezone: 2,
    currency: 'UYU',
    color: '#EF4444'
  }
];

export const REGION_COLORS = {
  north_america: '#3B82F6',    // Blue
  central_america: '#10B981',  // Green
  andean_region: '#F59E0B',    // Amber
  southern_cone: '#EF4444'     // Red
};

export const REGION_NAMES = {
  north_america: 'North America',
  central_america: 'Central America',
  andean_region: 'Andean Region',
  southern_cone: 'Southern Cone'
};

// Country flags (emoji)
export const COUNTRY_FLAGS: Record<string, string> = {
  CA: '🇨🇦',
  US: '🇺🇸',
  MX: '🇲🇽',
  GT: '🇬🇹',
  CR: '🇨🇷',
  PA: '🇵🇦',
  CO: '🇨🇴',
  VE: '🇻🇪',
  EC: '🇪🇨',
  PE: '🇵🇪',
  BO: '🇧🇴',
  BR: '🇧🇷',
  PY: '🇵🇾',
  CL: '🇨🇱',
  AR: '🇦🇷',
  UY: '🇺🇾'
};

// Get country by code
export function getCountryByCode(code: string): CountryData | undefined {
  return AMERICAS_COUNTRIES.find(c => c.code === code);
}

// Get countries by region
export function getCountriesByRegion(region: string): CountryData[] {
  if (region === 'all') return AMERICAS_COUNTRIES;
  return AMERICAS_COUNTRIES.filter(c => c.region === region);
}
