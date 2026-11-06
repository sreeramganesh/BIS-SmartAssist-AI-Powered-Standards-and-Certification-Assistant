export function getBISAnswer(promptText) {
  const query = promptText.toLowerCase();

  if (query.includes('charger') || query.includes('usb')) {
    return {
      paragraphs: [
        'Yes. Mobile phone power adaptors and chargers fall under the Compulsory Registration Scheme (CRS), administered by BIS under the Electronics and IT Goods Order.',
        'Manufacturers (both domestic and foreign) must register their models on the BIS CRS portal after testing at a BIS-recognized laboratory.'
      ],
      citation: {
        std: 'IS 13252 (Part 1) / IEC 60950-1 or IS 616',
        text: 'Information technology equipment — Safety requirements. Adaptors & power banks are mandatory CRS items.'
      },
      confidence: 'High confidence',
      risk: 'Verify HSN code with customs',
      steps: [
        'Get charger sample tested at a BIS-recognized lab against IS 13252.',
        'Apply for CRS registration on the BIS portal with the test report.',
        'Affix the R-number mark on product packaging prior to domestic sale.'
      ]
    };
  } else if (query.includes('mattress') || query.includes('foam')) {
    return {
      paragraphs: [
        'Flexible polyurethane foam mattresses fall under IS 7888 / IS 17981 standards.',
        'BIS has issued Quality Control Orders (QCO) making ISI certification compulsory for foam mattresses manufactured or imported into India.'
      ],
      citation: {
        std: 'IS 7888: Flexible Polyurethane Foam',
        text: 'Specifications for polyurethane foam mattresses & cushions for domestic and hospital applications.'
      },
      confidence: 'Verified QCO',
      risk: 'Non-certified stock subject to seizure',
      steps: [
        'Ensure factory quality control infrastructure aligns with IS 7888 Scheme of Inspection and Testing.',
        'Submit online ISI mark application on Manakonline portal.',
        'Schedule factory inspection by BIS officer for sample collection.'
      ]
    };
  }

  return {
    paragraphs: [
      `Regarding "${promptText}" — compliance depends on your specific product classification, intended application, and applicable Quality Control Orders (QCO).`,
      'Under BIS regulations, products fall either under the ISI Mark Scheme (Factory Inspection + Testing) or the Compulsory Registration Scheme (Self-Declaration + Lab Testing).'
    ],
    citation: {
      std: 'Bureau of Indian Standards Act, 2016',
      text: 'Governs mandatory certification mark schemes, laboratory testing protocols, and QCO enforcement across India.'
    },
    confidence: 'Standard Guidance',
    risk: 'Verify latest QCO gazette notification',
    steps: [
      'Identify exact Indian Standard (IS) code corresponding to your product.',
      'Check whether your product is covered under mandatory ISI scheme or CRS scheme.',
      'Engage a BIS-recognized laboratory for preliminary sample testing.'
    ]
  };
}

export function formatDateTime(d = new Date()) {
  const dateObj = new Date(d);
  return dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) +
    ' · ' + dateObj.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}
