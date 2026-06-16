const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { priceId, mode } = req.body;

  const allowed = [
    process.env.PRICE_WEEKLY,
    process.env.PRICE_MONTHLY,
    process.env.PRICE_YEARLY
  ];

  if (!allowed.includes(priceId)) {
    return res.status(400).json({ error: 'Invalid price' });
  }

  try {
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [{ price: priceId, quantity: 1 }],
      mode: mode === 'subscription' ? 'subscription' : 'payment',
      success_url: `${process.env.BASE_URL}?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.BASE_URL}?cancelled=true`,
    });

    res.status(200).json({ url: session.url });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
};
