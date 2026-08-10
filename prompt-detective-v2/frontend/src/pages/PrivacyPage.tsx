import React from 'react';

const PrivacyPage: React.FC = () => {
  return (
    <div className="bg-slate-50 py-16 dark:bg-[#050916]">
      <div className="mx-auto max-w-5xl px-6 lg:px-8">
        <header className="border-b border-slate-200 pb-10 dark:border-slate-800/80">
          <p className="text-xs font-semibold uppercase tracking-widest text-blue-600 dark:text-indigo-300">Legal</p>
          <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-4xl">
            Reverse AI Privacy Policy
          </h1>
          <p className="mt-3 max-w-3xl text-base text-slate-600 dark:text-white/80">
            This Privacy Policy explains how Reverse AI Labs ("Reverse AI", "we", "our", or
            "us") collects, uses, discloses, and protects personal information when you interact with our applications,
            websites, and related services (collectively, the "Services").
          </p>
          <p className="mt-3 text-xs text-slate-400 dark:text-white/60">Effective date: 16 September 2024. Last updated: 16 September 2024.</p>
        </header>

        <div className="prose prose-slate mt-12 max-w-none dark:prose-invert dark:prose-headings:text-white dark:prose-p:text-white/80 dark:prose-li:text-white/80 dark:prose-strong:text-white">
          <section>
            <h2>1. Information We Collect</h2>
            <ul>
              <li>
                <strong>Account information:</strong> Name, email address, password hash, and company details supplied
                during registration.
              </li>
              <li>
                <strong>Workspace data:</strong> Prompts, documents, media, and annotations you upload or generate while
                using the Services.
              </li>
              <li>
                <strong>Usage data:</strong> Log files, device metadata, IP addresses, browser types, and feature
                interactions collected to improve performance.
              </li>
              <li>
                <strong>Billing records:</strong> Payment instrument tokens, invoices, and subscription history managed via
                PCI-compliant payment processors.
              </li>
            </ul>
          </section>

          <section>
            <h2>2. How We Use Information</h2>
            <p>We process personal data to:</p>
            <ul>
              <li>Deliver and maintain the Services, including customer support and account management.</li>
              <li>Improve features, train quality algorithms, and develop new offerings.</li>
              <li>Send important communications, such as security alerts, billing notices, and product updates.</li>
              <li>Detect, investigate, and prevent fraud, abuse, and security incidents.</li>
              <li>Comply with legal obligations and enforce our Terms of Service.</li>
            </ul>
          </section>

          <section>
            <h2>3. Legal Bases for Processing</h2>
            <p>
              If you are located in the European Economic Area (EEA) or UK, we process your personal information under one
              or more of the following legal bases: performance of a contract, legitimate interests, compliance with legal
              obligations, or consent (which you may withdraw at any time).
            </p>
          </section>

          <section>
            <h2>4. Sharing & Disclosure</h2>
            <ul>
              <li>
                <strong>Service providers:</strong> We engage vetted vendors for hosting, analytics, customer support,
                email delivery, and secure payment processing.
              </li>
              <li>
                <strong>Law enforcement:</strong> We may share information in response to lawful requests or to protect
                prompt Detective, our users, or the public.
              </li>
              <li>
                <strong>Business transfers:</strong> In the event of a merger, acquisition, or asset sale, personal data may
                be transferred to the acquiring entity subject to this Policy.
              </li>
            </ul>
          </section>

          <section>
            <h2>5. International Data Transfers</h2>
            <p>
              Our infrastructure operates globally. When transferring data outside your jurisdiction, we implement
              safeguards such as Standard Contractual Clauses and regional data residency options for enterprise plans.
            </p>
          </section>

          <section>
            <h2>6. Data Retention</h2>
            <p>
              We retain personal information for as long as necessary to provide the Services, comply with legal
              obligations, and resolve disputes. Users may request deletion or export of Customer Data via the admin console
              or by contacting privacy@promptdetective.ai.
            </p>
          </section>

          <section>
            <h2>7. Security</h2>
            <p>
              We employ industry-standard security measures, including encryption in transit, tokenized authentication,
              role-based access, real-time anomaly detection, and regular penetration testing. No system is completely
              secure, so we encourage responsible disclosure of vulnerabilities following our security policy.
            </p>
          </section>

          <section>
            <h2>8. Your Rights</h2>
            <p>Depending on your jurisdiction, you may have rights to:</p>
            <ul>
              <li>Access and obtain a copy of your personal data.</li>
              <li>Request correction or deletion of inaccurate or unnecessary data.</li>
              <li>Restrict or object to certain processing.</li>
              <li>Data portability where technically feasible.</li>
              <li>Withdraw consent without affecting prior processing.</li>
            </ul>
            <p>
              Submit requests through the in-product privacy portal or via privacy@promptdetective.ai. We will respond
              within 30 days, subject to identity verification.
            </p>
          </section>

          <section>
            <h2>9. Children's Data</h2>
            <p>
              The Services are not directed to children under 16. We do not knowingly collect personal information from
              children. If you believe a child has provided personal data, please contact us so we can delete it.
            </p>
          </section>

          <section>
            <h2>10. Cookies & Similar Technologies</h2>
            <p>
              We use cookies, pixels, and local storage to authenticate users, personalize experiences, and measure
              engagement. You can adjust browser settings to block or delete cookies, though the Services may not function
              properly. Enterprise customers can request a cookie minimization policy specific to their deployment.
            </p>
          </section>

          <section>
            <h2>11. Privacy for AI & Model Training</h2>
            <p>
              Customer Data is not used to train public foundation models. For certain opt-in beta features, we may collect
              additional telemetry with your consent to improve performance. Aggregated or anonymized insights may be used
              to enhance the Services while ensuring individuals cannot be identified.
            </p>
          </section>

          <section>
            <h2>12. Communications Preferences</h2>
            <p>
              You may opt out of marketing emails at any time by using the unsubscribe link in the message or updating
              preferences in your account settings. Transactional communications (such as billing or security alerts) are
              considered essential to service delivery and cannot be opted out of.
            </p>
          </section>

          <section>
            <h2>13. Data Protection Officer</h2>
            <p>
              Prompt Detective has appointed a Data Protection Officer (DPO). Contact the DPO at dpo@promptdetective.ai for
              privacy inquiries, regulatory questions, or appeals relating to unresolved issues.
            </p>
          </section>

          <section>
            <h2>14. Changes to This Policy</h2>
            <p>
              We may update this Privacy Policy to reflect operational, legal, or regulatory changes. If we make material
              updates, we will notify you via email or in-product messaging. Continued use of the Services after the
              effective date constitutes acceptance of the revised Policy.
            </p>
          </section>

          <section>
            <h2>15. Contact</h2>
            <p>
              For questions or concerns about this Policy, contact privacy@promptdetective.ai or write to Prompt Detective
              Labs Private Limited, Bengaluru, India. EU/UK residents may also lodge a complaint with their local data
              protection authority.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPage;
