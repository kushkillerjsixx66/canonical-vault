const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { sessionId } = req.body;

  if (!sessionId) return res.status(400).json({ error: 'Missing session ID' });

  try {
    const session = await stripe.checkout.sessions.retrieve(sessionId, {
      expand: ['line_items']
    });

    if (session.payment_status === 'paid' || session.status === 'complete') {
      // Issue a simple access token: sessionId + timestamp signed loosely
      const token = Buffer.from(`${sessionId}:${Date.now()}:lattice`).toString('base64');
      return res.status(200).json({
        access: true,
        token,
        mode: session.mode,
        priceId: session.line_items?.data?.[0]?.price?.id || '',
        email: session.customer_details?.email || ''
      });
    }

    return res.status(402).json({ access: false, error: 'Payment not completed' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
};
