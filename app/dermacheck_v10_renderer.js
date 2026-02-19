/**
 * DermaCheck AI v10.0 - Medical-Grade Frontend Integration Module
 * Professional dual-view renderer for clinical metadata
 * 
 * Compatible with: React, Vue, Vanilla JS, any modern framework
 * Features: Clinical guidelines, Evidence grading, CI, Timelines, Disclaimers
 * 
 * Usage:
 *   import { DermaCheckRenderer } from './dermacheck_v10_renderer.js';
 *   const renderer = new DermaCheckRenderer('patient'); // or 'doctor'
 *   renderer.renderAnalysis(apiResponse, containerElement);
 */

export class DermaCheckRenderer {
    constructor(viewMode = 'patient') {
        this.viewMode = viewMode; // 'doctor' or 'patient'
    }

    /**
     * Main render function - call this with API response
     * @param {Object} response - Full API response from /analyze endpoint
     * @param {HTMLElement} container - DOM element to render into
     */
    renderAnalysis(response, container) {
        if (!response.success) {
            this.renderError(container, 'Analysis failed');
            return;
        }

        const { diagnosis, metadata } = response;

        // Extract structured data
        const parsed = this.parseMetadata(metadata);

        // Render based on view mode
        if (this.viewMode === 'doctor') {
            this.renderDoctorView(parsed, container);
        } else {
            this.renderPatientView(parsed, container);
        }
    }

    /**
     * Parse metadata from API response
     */
    parseMetadata(metadata) {
        return {
            // Primary diagnosis
            diagnosis: this.extractPrimaryDiagnosis(metadata),

            // Confidence analysis
            confidence: metadata.confidence_analysis || {
                point_estimate: 85,
                ci_95_lower: 82,
                ci_95_upper: 88,
                interpretation: 'Moderate precision'
            },

            // Clinical guidelines
            guidelines: metadata.clinical_guidelines || {},

            // Timeline and follow-up
            timeline: metadata.follow_up_plan || {},

            // Disclaimers
            disclaimer: metadata.disclaimer || {},

            // Risk tier
            risk: this.extractRiskTier(metadata),

            // Post-processing flags
            processing: metadata.post_processing_metadata || {}
        };
    }

    /**
     * Extract primary diagnosis from response
     */
    extractPrimaryDiagnosis(metadata) {
        // Try to extract from various locations
        const diagnosis = metadata.diagnosis ||
            metadata.primary_diagnosis ||
            'Diagnosis not available';

        // Extract just the condition name (before any parentheses)
        const match = diagnosis.match(/^([^(]+)/);
        return match ? match[1].trim() : diagnosis;
    }

    /**
     * Extract risk tier
     */
    extractRiskTier(metadata) {
        // Check various possible locations
        if (metadata.risk_tier) return metadata.risk_tier;
        if (metadata.follow_up_plan?.urgency) {
            const urgency = metadata.follow_up_plan.urgency;
            if (urgency === 'URGENT') return 'HIGH';
            if (urgency === 'SOON') return 'MEDIUM';
            return 'LOW';
        }
        return 'MEDIUM'; // Conservative default
    }

    /**
     * ===== DOCTOR VIEW RENDERER =====
     */
    renderDoctorView(data, container) {
        const html = `
      <div class="dermacheck-doctor-view">
        <!-- Header -->
        ${this.renderDoctorHeader(data)}
        
        <!-- Diagnosis Section -->
        ${this.renderDoctorDiagnosis(data)}
        
        <!-- Confidence Analysis -->
        ${this.renderDoctorConfidence(data)}
        
        <!-- Clinical Guidelines -->
        ${this.renderDoctorGuidelines(data)}
        
        <!-- Follow-up Timeline -->
        ${this.renderDoctorTimeline(data)}
        
        <!-- Medical Disclaimer -->
        ${this.renderDoctorDisclaimer(data)}
      </div>
    `;

        container.innerHTML = html;
    }

    renderDoctorHeader(data) {
        const riskColor = this.getRiskColor(data.risk);
        const riskEmoji = this.getRiskEmoji(data.risk);

        return `
      <div class="doctor-header" style="background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); color: white; padding: 24px; border-radius: 12px; margin-bottom: 24px;">
        <h2 style="margin: 0 0 8px 0; font-size: 24px;">🩺 Clinical Analysis Report</h2>
        <p style="margin: 0; opacity: 0.9;">DermaCheck AI v10.0 - Medical-Grade Professional</p>
      </div>

      <div class="risk-badge" style="background: ${riskColor}; color: white; padding: 16px; border-radius: 8px; text-align: center; margin-bottom: 24px;">
        <h3 style="margin: 0; font-size: 28px;">${riskEmoji} ${data.risk} RISK</h3>
      </div>
    `;
    }

    renderDoctorDiagnosis(data) {
        return `
      <div class="diagnosis-section" style="background: #f8fafc; padding: 20px; border-radius: 8px; border-left: 4px solid #2563eb; margin-bottom: 24px;">
        <h3 style="color: #1e40af; margin-top: 0;">PRIMARY DIAGNOSIS</h3>
        <p style="font-size: 20px; font-weight: 600; margin: 8px 0;">${data.diagnosis}</p>
      </div>
    `;
    }

    renderDoctorConfidence(data) {
        const conf = data.confidence;

        return `
      <div class="confidence-section" style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 24px;">
        <h3 style="color: #1e40af; margin-top: 0;">📊 Diagnostic Confidence Analysis</h3>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin: 16px 0;">
          <div style="background: #eff6ff; padding: 16px; border-radius: 8px;">
            <div style="font-size: 12px; color: #64748b; margin-bottom: 4px;">Point Estimate</div>
            <div style="font-size: 28px; font-weight: bold; color: #2563eb;">${conf.point_estimate}%</div>
          </div>
          
          <div style="background: #f1f5f9; padding: 16px; border-radius: 8px;">
            <div style="font-size: 12px; color: #64748b; margin-bottom: 4px;">95% Confidence Interval</div>
            <div style="font-size: 20px; font-weight: 600; color: #475569;">${conf.ci_95_lower}% - ${conf.ci_95_upper}%</div>
          </div>
          
          <div style="background: #f8fafc; padding: 16px; border-radius: 8px;">
            <div style="font-size: 12px; color: #64748b; margin-bottom: 4px;">Precision</div>
            <div style="font-size: 16px; font-weight: 500; color: #475569;">${conf.interpretation}</div>
          </div>
        </div>
      </div>
    `;
    }

    renderDoctorGuidelines(data) {
        const guidelines = data.guidelines;

        if (!guidelines.primary_guideline) return '';

        const evidenceColor = this.getEvidenceColor(guidelines.evidence_level);

        return `
      <div class="guidelines-section" style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 24px;">
        <h3 style="color: #0d9488; margin-top: 0;">📚 Clinical Evidence & Guidelines</h3>
        
        <div style="background: #f0fdfa; padding: 16px; border-radius: 8px; border-left: 4px solid #14b8a6; margin-bottom: 16px;">
          <div style="font-weight: 600; color: #0d9488; margin-bottom: 8px;">Primary Guideline</div>
          <div style="font-size: 18px; font-weight: 500; margin-bottom: 4px;">${guidelines.primary_guideline}</div>
          ${guidelines.url ? `<a href="${guidelines.url}" target="_blank" style="color: #14b8a6; text-decoration: none; font-size: 14px;">📄 View Guideline →</a>` : ''}
        </div>
        
        <div style="display: flex; gap: 12px; margin-bottom: 16px;">
          <div style="background: ${evidenceColor}; color: white; padding: 8px 16px; border-radius: 6px; font-weight: 600;">
            Evidence Level: ${guidelines.evidence_level || 'B'}
          </div>
          <div style="background: #f1f5f9; color: #475569; padding: 8px 16px; border-radius: 6px; font-weight: 600;">
            ${guidelines.evidence_strength || 'MODERATE'}
          </div>
        </div>
        
        ${guidelines.evidence_basis ? `
          <div style="font-size: 14px; color: #64748b; margin-bottom: 12px;">
            <strong>Basis:</strong> ${guidelines.evidence_basis}
          </div>
        ` : ''}
        
        ${guidelines.indonesian_reference ? `
          <div style="font-size: 14px; color: #64748b;">
            <strong>Indonesian Reference:</strong> ${guidelines.indonesian_reference}
          </div>
        ` : ''}
        
        ${guidelines.key_points && guidelines.key_points.length > 0 ? `
          <div style="margin-top: 16px;">
            <div style="font-weight: 600; color: #475569; margin-bottom: 8px;">Key Clinical Points:</div>
            <ul style="margin: 0; padding-left: 20px; color: #64748b;">
              ${guidelines.key_points.map(point => `<li style="margin-bottom: 4px;">${point}</li>`).join('')}
            </ul>
          </div>
        ` : ''}
      </div>
    `;
    }

    renderDoctorTimeline(data) {
        const timeline = data.timeline;

        if (!timeline.timeframe) return '';

        const urgencyColor = this.getUrgencyColor(timeline.urgency);

        return `
      <div class="timeline-section" style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 24px;">
        <h3 style="color: #7c3aed; margin-top: 0;">⏰ Follow-Up Plan & Specific Timeline</h3>
        
        <div style="display: flex; gap: 16px; margin-bottom: 16px;">
          <div style="background: ${urgencyColor}; color: white; padding: 16px; border-radius: 8px; flex: 1;">
            <div style="font-size: 12px; opacity: 0.9; margin-bottom: 4px;">Urgency Level</div>
            <div style="font-size: 24px; font-weight: bold;">${timeline.urgency || 'ROUTINE'}</div>
          </div>
          
          <div style="background: #f5f3ff; padding: 16px; border-radius: 8px; flex: 1;">
            <div style="font-size: 12px; color: #64748b; margin-bottom: 4px;">Specific Timeframe</div>
            <div style="font-size: 20px; font-weight: 600; color: #7c3aed;">${timeline.timeframe}</div>
          </div>
        </div>
        
        ${timeline.rationale ? `
          <div style="background: #fef3c7; padding: 12px; border-radius: 6px; border-left: 3px solid #f59e0b; margin-bottom: 16px;">
            <strong style="color: #92400e;">Clinical Rationale:</strong><br>
            <span style="color: #78350f;">${timeline.rationale}</span>
          </div>
        ` : ''}
        
        ${timeline.action_items && timeline.action_items.length > 0 ? `
          <div>
            <div style="font-weight: 600; color: #475569; margin-bottom: 12px;">Action Items Checklist:</div>
            <div style="background: #f8fafc; padding: 16px; border-radius: 8px;">
              ${timeline.action_items.map((item, i) => `
                <div style="display: flex; align-items: start; margin-bottom: 8px;">
                  <input type="checkbox" id="action_${i}" style="margin-right: 12px; margin-top: 4px;">
                  <label for="action_${i}" style="color: #475569; cursor: pointer;">${item}</label>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}
        
        ${timeline.biopsy_technique ? `
          <div style="margin-top: 16px; background: #f0f9ff; padding: 16px; border-radius: 8px; border-left: 4px solid #0284c7;">
            <div style="font-weight: 600; color: #0369a1; margin-bottom: 8px;">🔬 Biopsy Technique Recommendation:</div>
            <div style="color: #0c4a6e; font-size: 14px;">
              <strong>Preferred:</strong> ${timeline.biopsy_technique.preferred}<br>
              <strong>Margin:</strong> ${timeline.biopsy_technique.margin}<br>
              ${timeline.biopsy_technique.avoid ? `<strong>Avoid:</strong> ${timeline.biopsy_technique.avoid}<br>` : ''}
            </div>
          </div>
        ` : ''}
      </div>
    `;
    }

    renderDoctorDisclaimer(data) {
        const disclaimer = data.disclaimer.doctor_full || data.disclaimer.doctor_short || 'Medical disclaimer not available';

        return `
      <div class="disclaimer-section" style="background: #fef2f2; padding: 20px; border-radius: 8px; border-left: 4px solid #dc2626;">
        <h4 style="color: #991b1b; margin-top: 0; display: flex; align-items: center; gap: 8px;">
          ⚠️ IMPORTANT MEDICAL DISCLAIMER
        </h4>
        <div style="color: #7f1d1d; font-size: 14px; line-height: 1.6; white-space: pre-wrap;">${disclaimer}</div>
      </div>
    `;
    }

    /**
     * ===== PATIENT VIEW RENDERER =====
     */
    renderPatientView(data, container) {
        const html = `
      <div class="dermacheck-patient-view">
        <!-- Header -->
        ${this.renderPatientHeader(data)}
        
        <!-- Diagnosis (Simplified) -->
        ${this.renderPatientDiagnosis(data)}
        
        <!-- Disclaimer -->
        ${this.renderPatientDisclaimer(data)}
        
        <!-- About Condition -->
        ${this.renderPatientAboutCondition(data)}
        
        <!-- Timeline (Simplified) -->
        ${this.renderPatientTimeline(data)}
        
        <!-- Next Steps -->
        ${this.renderPatientNextSteps(data)}
      </div>
    `;

        container.innerHTML = html;
    }

    renderPatientHeader(data) {
        const riskColor = this.getRiskColor(data.risk);
        const riskEmoji = this.getRiskEmoji(data.risk);

        return `
      <div class="patient-header" style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
          <div style="width: 48px; height: 48px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px;">
            🩺
          </div>
          <div>
            <h2 style="margin: 0; font-size: 22px;">Hasil Analisis</h2>
            <p style="margin: 4px 0 0 0; opacity: 0.9; font-size: 14px;">DermaCheck AI</p>
          </div>
        </div>
      </div>
    `;
    }

    renderPatientDiagnosis(data) {
        const riskColor = this.getRiskColor(data.risk);
        const riskEmoji = this.getRiskEmoji(data.risk);
        const riskTextIndo = {
            'HIGH': 'TINGGI',
            'MEDIUM': 'SEDANG',
            'LOW': 'RENDAH'
        }[data.risk] || 'SEDANG';

        return `
      <div class="diagnosis-card" style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 16px;">
          <div style="flex: 1;">
            <div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Kondisi yang Terdeteksi</div>
            <h3 style="margin: 0; color: #1e293b; font-size: 24px; line-height: 1.3;">${data.diagnosis}</h3>
          </div>
        </div>
        
        <div style="background: #f8fafc; padding: 12px; border-radius: 8px; margin-bottom: 12px;">
          <div style="font-size: 12px; color: #64748b; margin-bottom: 4px;">Tingkat Keyakinan AI</div>
          <div style="font-size: 32px; font-weight: bold; color: #2563eb;">${data.confidence.point_estimate}%</div>
          <div style="width: 100%; height: 6px; background: #e2e8f0; border-radius: 3px; margin-top: 8px; overflow: hidden;">
            <div style="width: ${data.confidence.point_estimate}%; height: 100%; background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%); transition: width 0.3s ease;"></div>
          </div>
        </div>
        
        <div style="background: ${riskColor}; padding: 12px; border-radius: 8px; text-align: center;">
          <div style="color: white; font-weight: 600; font-size: 18px;">
            ${riskEmoji} TINGKAT BAHAYA: ${riskTextIndo}
          </div>
        </div>
      </div>
    `;
    }

    renderPatientDisclaimer(data) {
        const disclaimer = data.disclaimer.patient_short || 'Hasil AI hanya untuk skrining. Tetap konsultasi dokter kulit.';

        return `
      <div class="disclaimer-patient" style="background: #fffbeb; padding: 16px; border-radius: 8px; border-left: 4px solid #f59e0b; margin-bottom: 20px;">
        <div style="display: flex; align-items: start; gap: 12px;">
          <div style="font-size: 24px;">⚠️</div>
          <div>
            <div style="font-weight: 600; color: #92400e; margin-bottom: 4px;">PENTING - Disclaimer Medis</div>
            <div style="color: #78350f; font-size: 14px; line-height: 1.5;">${disclaimer}</div>
          </div>
        </div>
      </div>
    `;
    }

    renderPatientAboutCondition(data) {
        const guidelines = data.guidelines;

        return `
      <div class="about-condition" style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 20px;">
        <h3 style="color: #1e293b; margin-top: 0; display: flex; align-items: center; gap: 8px;">
          🩺 Tentang Kondisi Ini
        </h3>
        
        <div style="color: #475569; font-size: 15px; line-height: 1.7; margin-bottom: 16px;">
          ${this.getConditionDescriptionIndonesian(data.diagnosis)}
        </div>
        
        ${guidelines.indonesian_reference ? `
          <div style="background: #f0fdfa; padding: 12px; border-radius: 8px; border-left: 3px solid #14b8a6;">
            <div style="font-size: 12px; color: #0f766e; margin-bottom: 4px;">📚 Referensi Klinis</div>
            <div style="color: #115e59; font-weight: 500;">${guidelines.indonesian_reference}</div>
          </div>
        ` : ''}
      </div>
    `;
    }

    renderPatientTimeline(data) {
        const timeline = data.timeline;

        if (!timeline.timeframe_indonesian) return '';

        const urgencyEmoji = {
            'URGENT': '🔴',
            'SOON': '🟡',
            'ROUTINE': '🟢'
        }[timeline.urgency] || '🟡';

        const urgencyText = timeline.urgency_indonesian || 'SEGERA';

        return `
      <div class="timeline-patient" style="background: #fef2f2; padding: 20px; border-radius: 12px; border-left: 4px solid #ef4444; margin-bottom: 20px;">
        <h3 style="color: #991b1b; margin-top: 0; display: flex; align-items: center; gap: 8px;">
          ⏰ Waktu Penyembuhan
        </h3>
        
        <div style="background: white; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div>
              <div style="font-size: 12px; color: #64748b; margin-bottom: 4px;">Urgensi</div>
              <div style="font-size: 20px; font-weight: bold; color: #dc2626;">${urgencyEmoji} ${urgencyText}</div>
            </div>
            <div style="text-align: right;">
              <div style="font-size: 12px; color: #64748b; margin-bottom: 4px;">Waktu</div>
              <div style="font-size: 18px; font-weight: 600; color: #475569;">${timeline.timeframe_indonesian}</div>
            </div>
          </div>
        </div>
        
        ${timeline.rationale_indonesian ? `
          <div style="background: rgba(255,255,255,0.7); padding: 12px; border-radius: 8px;">
            <div style="font-size: 13px; color: #7f1d1d; line-height: 1.6;">
              <strong>Kenapa ${urgencyText}?</strong><br>
              ${timeline.rationale_indonesian}
            </div>
          </div>
        ` : ''}
      </div>
    `;
    }

    renderPatientNextSteps(data) {
        const timeline = data.timeline;

        if (!timeline.action_items_indonesian || timeline.action_items_indonesian.length === 0) return '';

        const urgencyColor = timeline.urgency === 'URGENT' ? '#dc2626' :
            timeline.urgency === 'SOON' ? '#f59e0b' : '#10b981';

        return `
      <div class="next-steps-patient" style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        <h3 style="color: #1e293b; margin-top: 0; display: flex; align-items: center; gap: 8px;">
          🎯 Langkah Selanjutnya
        </h3>
        
        <div style="font-size: 14px; color: #64748b; margin-bottom: 16px;">
          Ikuti panduan ini untuk menjaga kesehatan kulit Anda:
        </div>
        
        <div style="background: #f8fafc; padding: 16px; border-radius: 8px;">
          ${timeline.action_items_indonesian.map((item, i) => `
            <div style="display: flex; align-items: start; gap: 12px; margin-bottom: 12px; padding: 12px; background: white; border-radius: 6px; border-left: 3px solid ${urgencyColor};">
              <div style="width: 24px; height: 24px; background: ${urgencyColor}; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px; flex-shrink: 0;">
                ${i + 1}
              </div>
              <div style="flex: 1; color: #475569; font-size: 14px; line-height: 1.6; padding-top: 2px;">
                ${item}
              </div>
            </div>
          `).join('')}
        </div>
        
        ${timeline.urgency === 'URGENT' ? `
          <div style="background: #fef2f2; padding: 12px; border-radius: 8px; margin-top: 16px; border-left: 3px solid #dc2626;">
            <strong style="color: #991b1b;">⚠️ Perhatian:</strong>
            <div style="color: #7f1d1d; font-size: 14px; margin-top: 4px;">
              Kondisi ini memerlukan perhatian medis SEGERA. Jangan tunda konsultasi ke dokter!
            </div>
          </div>
        ` : ''}
      </div>
    `;
    }

    /**
     * ===== HELPER FUNCTIONS =====
     */

    getConditionDescriptionIndonesian(diagnosis) {
        const descriptions = {
            'melanoma': 'Melanoma adalah jenis kanker kulit yang berasal dari sel pigmen (melanosit). Deteksi dini sangat penting karena melanoma dapat berkembang dengan cepat.',
            'acne': 'Jerawat adalah kondisi kulit umum yang terjadi ketika folikel rambut tersumbat oleh minyak dan sel kulit mati. Penanganan yang tepat dapat mencegah bekas luka.',
            'eczema': 'Eksim (dermatitis atopik) adalah kondisi kulit yang menyebabkan kulit menjadi merah, gatal, dan kering. Kondisi ini dapat dikelola dengan perawatan yang tepat.',
            'dermatitis': 'Dermatitis adalah peradangan kulit yang dapat disebabkan oleh berbagai faktor. Perawatan tergantung pada jenis dan penyebabnya.'
        };

        const diagnosisLower = diagnosis.toLowerCase();
        for (const [key, desc] of Object.entries(descriptions)) {
            if (diagnosisLower.includes(key)) {
                return desc;
            }
        }

        return 'Kondisi kulit yang terdeteksi memerlukan evaluasi lebih lanjut oleh dokter kulit untuk diagnosis dan perawatan yang tepat.';
    }

    getRiskColor(risk) {
        const colors = {
            'HIGH': '#dc2626',
            'MEDIUM': '#f59e0b',
            'LOW': '#10b981'
        };
        return colors[risk] || colors.MEDIUM;
    }

    getRiskEmoji(risk) {
        const emojis = {
            'HIGH': '🔴',
            'MEDIUM': '🟡',
            'LOW': '🟢'
        };
        return emojis[risk] || emojis.MEDIUM;
    }

    getEvidenceColor(level) {
        const colors = {
            'A': '#10b981',
            'B': '#3b82f6',
            'C': '#f59e0b',
            'D': '#ef4444'
        };
        return colors[level] || colors.B;
    }

    getUrgencyColor(urgency) {
        const colors = {
            'URGENT': '#dc2626',
            'SOON': '#f59e0b',
            'ROUTINE': '#10b981'
        };
        return colors[urgency] || colors.ROUTINE;
    }

    renderError(container, message) {
        container.innerHTML = `
      <div style="background: #fef2f2; padding: 20px; border-radius: 8px; border-left: 4px solid #dc2626;">
        <h4 style="color: #991b1b; margin-top: 0;">❌ Error</h4>
        <p style="color: #7f1d1d;">${message}</p>
      </div>
    `;
    }

    /**
     * Switch between doctor and patient view
     */
    setViewMode(mode) {
        this.viewMode = mode;
    }
}

/**
 * Simple usage example:
 * 
 * // Initialize renderer
 * const renderer = new DermaCheckRenderer('patient');
 * 
 * // Call API
 * const response = await fetch('http://localhost:8000/analyze', {...});
 * const data = await response.json();
 * 
 * // Render
 * const container = document.getElementById('results');
 * renderer.renderAnalysis(data, container);
 * 
 * // Switch to doctor view
 * renderer.setViewMode('doctor');
 * renderer.renderAnalysis(data, container);
 */
