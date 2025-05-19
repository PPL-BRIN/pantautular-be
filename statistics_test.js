import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Trend, Rate } from 'k6/metrics';

// Kustom metrik untuk analisis
const statisticsApiCalls = new Counter('statistics_api_calls');
const statisticsApiErrors = new Counter('statistics_api_errors');
const statisticsApiLatency = new Trend('statistics_api_latency');
const statisticsApiErrorRate = new Rate('statistics_api_error_rate');

// Konfigurasi test
export const options = {
  // Tambahkan batasan resource
  maxRedirects: 0,          // Hindari redirects yang bisa mengkonsumsi resource
  discardResponseBodies: false, // Abaikan response body untuk menghemat memori

  thresholds: {
    'http_req_duration': ['p(95)<5000'], // 95% request selesai dalam 5 detik
    'http_req_failed': ['rate<0.1'],     // Error rate < 10%
  },
  
  // Gunakan hanya skenario untuk menentukan eksekusi
  scenarios: {
    main: {
      executor: 'ramping-vus',
      gracefulStop: '30s',
      gracefulRampDown: '30s',
      exec: 'default',
      // Letakkan stages di dalam skenario
      stages: [
        { duration: '30s', target: 10 },     // Warm-up: Tingkatkan ke 10 pengguna
        { duration: '1m', target: 10 },      // Stabil 10 pengguna
        { duration: '30s', target: 30 },     // Tingkatkan ke 30 pengguna
        { duration: '1m', target: 30 },      // Stabil 30 pengguna
        { duration: '30s', target: 50 },     // Tingkatkan ke 50 pengguna
        { duration: '1m', target: 50 },      // Stabil 50 pengguna
        { duration: '30s', target: 100 },    // Tingkatkan ke 100 pengguna
        { duration: '1m', target: 100 },     // Stabil 100 pengguna
        { duration: '30s', target: 150 },    // Tingkatkan ke 150 pengguna
        { duration: '1m', target: 150 },     // Stabil 150 pengguna
        { duration: '30s', target: 0 },      // Ramp-down ke 0
      ]
    },
  },
};

// Filter yang akan diuji
const filterConfigurations = [
  { name: "No Filter", data: {} },
  { 
    name: "Disease Filter", 
    data: { "diseases": ["Mpox"] } 
  },
  { 
    name: "Location Filter", 
    data: { "locations": {
      "provinces": ["Riau"],
      "cities":["Jakarta"]
     } 
    } 
  },
  { 
    name: "Level Filter", 
    data: { "level_of_alertness": 3 } 
  },
  { 
    name: "Portal Filter", 
    data: { "portals": ["Kompas", "Detik"] } 
  },
  { 
    name: "Date Range Filter", 
    data: { 
      "date_range": { 
        "start": getDateString(30), 
        "end": getDateString(0) 
      } 
    } 
  },
  { 
    name: "Complex Filter", 
    data: { 
      "diseases": ["Covid-19"],
      "locations": {
        "provinces": ["Riau"],
        "cities":["Jakarta"]
      },
      "level_of_alertness": 3,
      "portals": ["Kompas"],
      "date_range": { 
        "start": getDateString(30), 
        "end": getDateString(0) 
      }
    } 
  }
];

// Helper function untuk membuat string tanggal
function getDateString(daysAgo) {
  const date = new Date();
  date.setDate(date.getDate() - daysAgo);
  return date.toISOString().split('T')[0];
}

// Fungsi default yang dijalankan untuk setiap virtual user
const baseURL = 'http://localhost:8000';
const API_KEY = __ENV.SECRET_API_KEY || 'default_api_key'; // Gunakan API key dari environment variable atau default
export default function() {
  // Headers untuk request
  const headers = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json',
  };

  const params = {
    headers: headers,
    timeout: '10s', // Timeout lebih lama untuk menangani beban tinggi
    tags: { endpoint: 'statistics' },
  };

  // Pilih secara acak antara GET dan POST
  const usePost = Math.random() > 0.3; // NOSONAR - This is only used to vary test scenarios and has no security implications
  // 70% POST, 30% GET
  
  let response;
  const startTime = new Date().getTime();
  
  try {
    // Increment counter untuk panggilan API
    statisticsApiCalls.add(1);
    
    if (usePost) {
      // Untuk beban tinggi, gunakan filter sederhana lebih sering
      const simpleFilters = [0, 1, 2]; // Indeks untuk filter yang lebih ringan
      const complexFilters = [3, 4, 5, 6]; // Indeks untuk filter yang lebih kompleks
      
      // 70% filter sederhana, 30% kompleks saat beban tinggi
      let filterIndices;
      if (__VU > 50) {
        filterIndices = Math.random() > 0.3 ? simpleFilters : complexFilters; // NOSONAR - This is only used to vary test scenarios and has no security implications
      } else {
        filterIndices = [...simpleFilters, ...complexFilters]; // Semua filter untuk beban rendah
      }
      
      const filterIndex = filterIndices[Math.floor(Math.random() * filterIndices.length)]; // NOSONAR - This is only used to vary test scenarios and has no security implications
      const filterConfig = filterConfigurations[filterIndex];
      
      // console.log(`Testing with ${filterConfig.name} (VU: ${__VU})`);
      
      response = http.post(
        `${baseURL}/api/statistics/`,
        JSON.stringify(filterConfig.data),
        params
      );
    } else {
      // GET request tanpa filter
      response = http.get(
        `${baseURL}/api/statistics/`,
        params
      );
    }
    
    // Catat latency
    const latency = new Date().getTime() - startTime;
    statisticsApiLatency.add(latency);

    if (response.status === 200) {
      console.log(`Request success: ${response.status}, Body length: ${response.body ? response.body.length : 0}`);
      // Untuk debug, print bagian awal body
      if (response.body && response.body.length > 0) {
        console.log(`Body preview: ${response.body.substring(0, 50)}...`);
      }
    }
    
    // Periksa response
    const success = check(response, {
      'Status is 200': (r) => r.status === 200,
      'Has valid response': (r) => {
        if (r.status !== 200) return false;
        
        // Validasi lebih defensif
        try {
          if (!r.body || r.body.length === 0) {
            console.log(`Empty body received with status ${r.status}`);
            return false;
          }
          const body = JSON.parse(r.body);
          const hasData = body && body.hasOwnProperty('prevalence_statistics');
          if (!hasData) {
            console.log(`Missing prevalence_statistics in response: ${JSON.stringify(body).substring(0, 100)}...`);
          }
          return hasData;
        } catch (e) {
          console.log(`Error parsing response: ${e.message}, body: ${r.body?.substring(0, 50) || 'Empty'}`);
          return false;
        }
      }
    });
    
    // Catat error dan error rate
    if (!success) {
      statisticsApiErrors.add(1);
      statisticsApiErrorRate.add(1);
      console.log(`Error: Status ${response.status}, Body: ${response?.body?.substring(0, 100) || 'Empty'}`);
    } else {
      statisticsApiErrorRate.add(0);
    }
  } catch (error) {
    console.log(`Exception: ${error.message}`);
    statisticsApiErrors.add(1);
    statisticsApiErrorRate.add(1);
  }
  
  // Jeda antar-request yang berbeda sesuai tingkat beban
  if (__VU > 100) {
    sleep(Math.random() * 3 + 3); // NOSONAR - This is only used to vary test scenarios and has no security implications
    // // 3-6 detik untuk beban sangat tinggi
  } else if (__VU > 50) {
    sleep(Math.random() * 2 + 2); // NOSONAR - This is only used to vary test scenarios and has no security implications
    // 2-4 detik untuk beban tinggi
  } else {
    sleep(Math.random() * 2 + 1); // NOSONAR - This is only used to vary test scenarios and has no security implications
    // 1-3 detik untuk beban normal
  }
}