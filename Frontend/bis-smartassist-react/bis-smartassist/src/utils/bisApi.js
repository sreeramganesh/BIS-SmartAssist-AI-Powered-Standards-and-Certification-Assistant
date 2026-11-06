import { getBISAnswer } from './bisAnswers';

// Use environment-configured backend URL with fallback
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Parses raw RAG & LLM response into structured Thread display objects
 */
export function parseRAGResponse(data, originalQuestion) {
  const answerText = (data.answer || '').trim();
  const confidenceScore = typeof data.confidence === 'number' ? data.confidence : 0;
  const sources = Array.isArray(data.sources) ? data.sources : [];
  const uploadedFiles = Array.isArray(data.uploaded_files) ? data.uploaded_files : [];

  if (!answerText) {
    return {
      paragraphs: ['No response generated. Please verify your query or try again.'],
      confidence: 'Unverified',
      sources: [],
      uploaded_files: uploadedFiles
    };
  }

  // Parse structured sections if returned from prompt template
  const sectionHeaders = [
    'PRODUCT / QUERY',
    'UPLOADED DOCUMENT FINDINGS',
    'APPLICABLE INDIAN STANDARDS',
    'CERTIFICATION & COMPLIANCE',
    'CERTIFICATION',
    'TESTING & SPECIFICATIONS',
    'TESTING',
    'DOCUMENTATION',
    'IMPORTANT NOTES',
    'SOURCE SUMMARY'
  ];

  const sections = {};
  let currentHeader = 'GENERAL';
  sections[currentHeader] = [];

  const lines = answerText.split('\n');
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;

    const matchedHeader = sectionHeaders.find(
      h => trimmed.toUpperCase() === h || trimmed.toUpperCase().startsWith(h + ':')
    );

    if (matchedHeader) {
      currentHeader = matchedHeader;
      sections[currentHeader] = [];
    } else {
      sections[currentHeader].push(trimmed);
    }
  }

  const hasStructuredSections = Object.keys(sections).length > 2;

  let paragraphs = [];
  let stdText = '';
  let riskText = '';
  let steps = [];

  if (hasStructuredSections) {
    if (sections['GENERAL'] && sections['GENERAL'].length > 0) {
      paragraphs.push(sections['GENERAL'].join(' '));
    }
    if (sections['PRODUCT / QUERY'] && sections['PRODUCT / QUERY'].length > 0) {
      paragraphs.push(sections['PRODUCT / QUERY'].join(' '));
    }
    if (sections['UPLOADED DOCUMENT FINDINGS'] && sections['UPLOADED DOCUMENT FINDINGS'].length > 0) {
      paragraphs.push(`Document Analysis: ${sections['UPLOADED DOCUMENT FINDINGS'].join(' ')}`);
    }
    if (sections['CERTIFICATION & COMPLIANCE'] && sections['CERTIFICATION & COMPLIANCE'].length > 0) {
      paragraphs.push(`Certification & Compliance: ${sections['CERTIFICATION & COMPLIANCE'].join(' ')}`);
    } else if (sections['CERTIFICATION'] && sections['CERTIFICATION'].length > 0) {
      paragraphs.push(`Certification: ${sections['CERTIFICATION'].join(' ')}`);
    }
    if (sections['DOCUMENTATION'] && sections['DOCUMENTATION'].length > 0) {
      paragraphs.push(`Documentation & Traceability: ${sections['DOCUMENTATION'].join(' ')}`);
    }

    if (sections['APPLICABLE INDIAN STANDARDS'] && sections['APPLICABLE INDIAN STANDARDS'].length > 0) {
      stdText = sections['APPLICABLE INDIAN STANDARDS'].join(' · ');
    }

    if (sections['IMPORTANT NOTES'] && sections['IMPORTANT NOTES'].length > 0) {
      riskText = sections['IMPORTANT NOTES'].join(' ');
    }

    const testSection = sections['TESTING & SPECIFICATIONS'] || sections['TESTING'];
    if (testSection && testSection.length > 0) {
      steps = testSection
        .map(s => s.replace(/^[-*•\d.)\s]+/, '').trim())
        .filter(s => s.length > 0 && !s.toLowerCase().includes('no specific'));
    }
  } else {
    // Standard paragraph format
    paragraphs = answerText
      .split(/\n{2,}/)
      .map(p => p.trim())
      .filter(Boolean);
  }

  // Fallback for Indian Standard citations from sources if not in text
  if (!stdText && sources.length > 0) {
    const standardsFound = sources
      .filter(s => s.type === 'bis_knowledge_base' && s.standard)
      .map(s => s.standard);
    if (standardsFound.length > 0) {
      stdText = [...new Set(standardsFound)].slice(0, 3).join(' · ');
    }
  }

  // Fallback citation text
  let citation = null;
  if (stdText) {
    const bisSource = sources.find(s => s.type === 'bis_knowledge_base');
    citation = {
      std: stdText,
      text: bisSource?.source
        ? `Reference source: ${bisSource.source} (page ${bisSource.page || 'N/A'})`
        : 'Governing Bureau of Indian Standards & QCO Specifications'
    };
  } else if (sources.length > 0 && sources[0].source) {
    citation = {
      std: sources[0].standard || (sources[0].type === 'uploaded_document' ? 'User Document' : 'BIS Knowledge Base'),
      text: `${sources[0].source} (Page ${sources[0].page || '1'})`
    };
  }

  // Format confidence tag
  let confidenceLabel = 'General BIS Guidance';
  if (confidenceScore >= 75) {
    confidenceLabel = `High Confidence (${confidenceScore}%)`;
  } else if (confidenceScore >= 45) {
    confidenceLabel = `Verified Match (${confidenceScore}%)`;
  } else if (confidenceScore > 0) {
    confidenceLabel = `Relevant (${confidenceScore}%)`;
  }

  return {
    paragraphs: paragraphs.length > 0 ? paragraphs : [answerText],
    citation: citation,
    confidence: confidenceLabel,
    risk: riskText ? (riskText.length > 140 ? riskText.substring(0, 137) + '…' : riskText) : null,
    steps: steps.length > 0 ? steps : null,
    sources: sources,
    uploaded_files: uploadedFiles,
    isLive: true
  };
}

/**
 * Sends a text-only chat query to the FastAPI RAG backend with fallback to local mock
 */
export async function sendChatToBIS(question) {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 90000); // 90s timeout for local LLM

    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ question }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errMsg = `Backend returned HTTP status ${response.status}`;
      try {
        const errJson = await response.json();
        if (errJson && errJson.detail) errMsg = errJson.detail;
      } catch (_) {}
      throw new Error(errMsg);
    }

    const data = await response.json();
    return parseRAGResponse(data, question);
  } catch (error) {
    console.warn('Backend unavailable or failed. Using fallback BIS logic:', error.message);

    // Fallback to offline mock logic
    const mockData = getBISAnswer(question);
    return {
      ...mockData,
      confidence: `${mockData.confidence || 'Standard Guidance'} (Offline Mode)`,
      sources: [
        {
          source: 'BIS Act & Compulsory Quality Control Orders (Gazette)',
          page: 'Summary',
          standard: mockData.citation?.std || 'BIS CRS / ISI',
          type: 'bis_knowledge_base'
        }
      ],
      isLive: false,
      offlineNotice: `Backend server at ${API_BASE_URL} was unreachable. Displaying cached standard guidance.`
    };
  }
}

/**
 * Sends a multimodal query with uploaded files to /api/chat-with-files using multipart/form-data
 */
export async function sendChatWithFilesToBIS(question, fileObjects) {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 90000); // 90s timeout for local LLM

    const formData = new FormData();
    formData.append('question', question || '');
    for (const file of fileObjects) {
      formData.append('files', file);
    }

    // Notice: Do NOT manually set 'Content-Type': allow browser to generate boundary
    const response = await fetch(`${API_BASE_URL}/api/chat-with-files`, {
      method: 'POST',
      body: formData,
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errMsg = `Backend returned HTTP status ${response.status}`;
      try {
        const errJson = await response.json();
        if (errJson && errJson.detail) errMsg = errJson.detail;
      } catch (_) {}
      throw new Error(errMsg);
    }

    const data = await response.json();
    return parseRAGResponse(data, question);
  } catch (error) {
    console.warn('Backend chat-with-files failed. Using fallback logic:', error.message);

    const mockData = getBISAnswer(question || 'Uploaded document compliance inquiry');
    return {
      ...mockData,
      confidence: `${mockData.confidence || 'Standard Guidance'} (Offline Mode)`,
      sources: [
        {
          source: fileObjects[0]?.name || 'Uploaded Document',
          page: 1,
          standard: 'User Attachment',
          type: 'uploaded_document'
        },
        {
          source: 'BIS Act & Compulsory Quality Control Orders (Gazette)',
          page: 'Summary',
          standard: mockData.citation?.std || 'BIS CRS / ISI',
          type: 'bis_knowledge_base'
        }
      ],
      uploaded_files: fileObjects.map(f => ({
        filename: f.name,
        status: 'fallback'
      })),
      isLive: false,
      offlineNotice: `Backend endpoint at ${API_BASE_URL}/api/chat-with-files was unreachable (${error.message}). Displaying fallback guidance.`
    };
  }
}
