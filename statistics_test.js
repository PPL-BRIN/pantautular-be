import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Trend, Rate } from 'k6/metrics';

// Custom metrics for analysis
const statisticsApiCalls = new Counter('statistics_api_calls');
const statisticsApiErrors = new Counter('statistics_api_errors');
const statisticsApiLatency = new Trend('statistics_api_latency');
const statisticsApiErrorRate = new Rate('statistics_api_error_rate');

// Test configuration
export const options = {
  // Same configuration as before
  maxRedirects: 0,
  discardResponseBodies: false,
  thresholds: {
    'http_req_duration': ['p(95)<5000'],
    'http_req_failed': ['rate<0.1'],
  },
  scenarios: {
    main: {
      executor: 'ramping-vus',
      gracefulStop: '30s',
      gracefulRampDown: '30s',
      exec: 'default',
      stages: [
        { duration: '30s', target: 10 },
        { duration: '1m', target: 10 },
        { duration: '30s', target: 30 },
        { duration: '1m', target: 30 },
        { duration: '30s', target: 50 },
        { duration: '1m', target: 50 },
        { duration: '30s', target: 100 },
        { duration: '1m', target: 100 },
        { duration: '30s', target: 150 },
        { duration: '1m', target: 150 },
        { duration: '30s', target: 0 },
      ]
    },
  },
};

// Filter configurations - unchanged
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

// Helper function for date string creation
function getDateString(daysAgo) {
  const date = new Date();
  date.setDate(date.getDate() - daysAgo);
  return date.toISOString().split('T')[0];
}

// Helper function for selecting filter
function selectFilterConfig(vuCount) {
  const simpleFilters = [0, 1, 2]; // Indices for lighter filters
  const complexFilters = [3, 4, 5, 6]; // Indices for more complex filters
  
  // Determine filter pool based on VU count
  const filterIndices = vuCount > 50 
    ? (Math.random() > 0.3 ? simpleFilters : complexFilters) // NOSONAR - Test scenario variation only
    : [...simpleFilters, ...complexFilters]; // All filters for low load
  
  const filterIndex = filterIndices[Math.floor(Math.random() * filterIndices.length)]; // NOSONAR - Test scenario variation only
  return filterConfigurations[filterIndex];
}

// Helper function to validate response
function validateResponse(response) {
  if (response.status !== 200) return false;
  
  try {
    if (!response.body || response.body.length === 0) {
      console.log(`Empty body received with status ${response.status}`);
      return false;
    }
    
    const body = JSON.parse(response.body);
    // Using optional chaining
    const hasData = body?.prevalence_statistics !== undefined;
    
    if (!hasData) {
      console.log(`Missing prevalence_statistics in response: ${JSON.stringify(body).substring(0, 100)}...`);
    }
    
    return hasData;
  } catch (e) {
    console.log(`Error parsing response: ${e.message}, body: ${response.body?.substring(0, 50) || 'Empty'}`);
    return false;
  }
}

// Helper function for sleep duration
function getSleepDuration(vuCount) {
  if (vuCount > 100) {
    return Math.random() * 3 + 3; // NOSONAR - Test scenario variation only
  } else if (vuCount > 50) {
    return Math.random() * 2 + 2; // NOSONAR - Test scenario variation only
  }
  return Math.random() * 2 + 1; // NOSONAR - Test scenario variation only
}

// Main test function
const baseURL = 'http://localhost:8000';
const API_KEY = __ENV.SECRET_API_KEY || 'default_api_key';

// Refactored default function with reduced complexity
export default function() {
  // Common setup
  const headers = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json',
  };

  const params = {
    headers: headers,
    timeout: '10s',
    tags: { endpoint: 'statistics' },
  };

  // Call increment counter for API
  statisticsApiCalls.add(1);
  
  // Track timing
  const startTime = new Date().getTime();
  
  // Determine request type (GET vs POST)
  const usePost = Math.random() > 0.3; // NOSONAR - Test scenario variation only
  
  try {
    const response = executeRequest(usePost, params);
    processResponse(response, startTime);
  } catch (error) {
    console.log(`Exception: ${error.message}`);
    statisticsApiErrors.add(1);
    statisticsApiErrorRate.add(1);
  }
  
  // Sleep between requests
  sleep(getSleepDuration(__VU));
}

// Helper function to execute the request
function executeRequest(usePost, params) {
  if (usePost) {
    // Select filter based on virtual user count
    const filterConfig = selectFilterConfig(__VU);
    console.log(`Testing with ${filterConfig.name} (VU: ${__VU})`);
    
    return http.post(
      `${baseURL}/api/statistics/`,
      JSON.stringify(filterConfig.data),
      params
    );
  } else {
    // GET request without filters
    return http.get(
      `${baseURL}/api/statistics/`,
      params
    );
  }
}

// Helper function to process the response
function processResponse(response, startTime) {
  // Record latency
  const latency = new Date().getTime() - startTime;
  statisticsApiLatency.add(latency);

  if (response.status === 200) {
    console.log(`Request success: ${response.status}, Body length: ${response.body?.length || 0}`);
    // For debug, print beginning of body
    if (response.body?.length > 0) {
      console.log(`Body preview: ${response.body.substring(0, 50)}...`);
    }
  }
  
  // Check response
  const success = check(response, {
    'Status is 200': (r) => r.status === 200,
    'Has valid response': (r) => validateResponse(r)
  });
  
  // Record error and error rate
  if (!success) {
    statisticsApiErrors.add(1);
    statisticsApiErrorRate.add(1);
    console.log(`Error: Status ${response.status}, Body: ${response?.body?.substring(0, 100) || 'Empty'}`);
  } else {
    statisticsApiErrorRate.add(0);
  }
}