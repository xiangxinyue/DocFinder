// For Vercel projects, add this API proxy
// Create a file: /api/proxy.js

export default async function handler(req, res) {
    // Set CORS headers
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Access-Control-Allow-Origin', 'https://doc-finder-ecru.vercel.app');
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
    res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');
  
    // Handle OPTIONS requests
    if (req.method === 'OPTIONS') {
      res.status(200).end();
      return;
    }
    
    if (req.method === 'POST') {
      try {
        // Forward the request to the backend
        const backendUrl = 'https://docfinder-u8c5.onrender.com/query';
        
        const response = await fetch(backendUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(req.body),
        });
        
        // Get backend response
        const data = await response.json();
        
        // Return backend response
        res.status(200).json(data);
      } catch (error) {
        console.error('Proxy error:', error);
        res.status(500).json({ error: 'Failed to proxy request', details: error.message });
      }
    } else {
      // Other request methods
      res.setHeader('Allow', 'POST, OPTIONS');
      res.status(405).end('Method Not Allowed');
    }
  }