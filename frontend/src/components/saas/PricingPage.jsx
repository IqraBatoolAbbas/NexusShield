import React from "react";

const plans = [
  ["Developer Free", "$0", "1,000 prompts / month", "For prototypes and local development"],
  ["Startup Pro", "$99", "100,000 prompts / month", "For production teams shipping AI"],
  ["Enterprise Custom", "Let's talk", "Unlimited scale", "For regulated, multi-tenant estates"],
];

export default function PricingPage({ onGetStarted }) {
  return <section className="content-section pricing-page"><div className="section-intro"><div><span className="section-kicker">NEXUSSHIELD CLOUD</span><h2>Security that scales with your AI.</h2><p>Start free, deploy at the edge, and upgrade when your traffic demands it.</p></div></div><div className="pricing-grid">{plans.map(([name, price, quota, description]) => <article className="panel pricing-card" key={name}><span className="section-kicker">{name}</span><strong>{price}</strong><b>{quota}</b><p>{description}</p><button onClick={onGetStarted}>GET STARTED</button></article>)}</div></section>;
}
