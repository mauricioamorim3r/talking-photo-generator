#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  Video and audio generation app from images using Gemini for analysis, Fal.ai (Veo 3, Sora 2, Wav2Lip) and HuggingFace for video generation, and ElevenLabs for audio. 
  Admin panel for API usage/costs tracking. Gallery for generated content management.
  Recent task: Integrate model-specific prompt templates for Sora 2 and Veo 3 from Fal.ai documentation while ensuring strict content policy compliance (no facial fidelity mentions).

backend:
  - task: "Model-specific prompt generation (Sora 2 & Veo 3)"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: |
          Implemented new model-specific prompt templates in Gemini system message:
          - Sora 2 template: Focuses on physics realism, character consistency, detailed environments
          - Veo 3 template: Focuses on cinematic quality, advanced audio synthesis, motion realism
          - Removed ALL references to facial fidelity/identity preservation from system prompt
          - Updated JSON response structure: prompt_sora2, prompt_veo3, prompt_economico, cinematic_details
          - Updated timeout fallback to match new structure
          - Kept aggressive sanitization as safety net
      - working: true
        agent: "testing"
        comment: |
          COMPREHENSIVE TESTING COMPLETED - ALL TESTS PASSED (24/24 - 100% success rate)
          
          ✅ JSON Structure Verification:
          - All required fields present: prompt_sora2, prompt_veo3, prompt_economico, cinematic_details
          - Cinematic details contains all required fields: subject_action, camera_work, lighting, audio_design, style
          - recommended_model_premium and recommended_model_economico fields present
          
          ✅ Model-Specific Prompt Generation:
          - Sora 2 prompts follow correct template (physics, movement, audio, 4K quality)
          - Veo 3 prompts follow correct template (cinematic shots, lens specs, lighting design, color grading, hyper-realistic)
          - Prompts are significantly different (19% similarity - sufficiently distinct)
          - Sora 2 average length: ~400 chars, Veo 3 average length: ~600 chars
          
          ✅ Content Policy Compliance:
          - ZERO facial fidelity violations detected in all generated prompts
          - NO forbidden terms found: "identidade facial", "fidelidade facial", "preservar", "100%", "características originais"
          - Aggressive sanitization working correctly - tested with problematic input, output was completely clean
          - Violent/threatening terms properly replaced with neutral alternatives
          
          ✅ Template Compliance Analysis:
          - Sora 2 elements verified: physics/movement, camera work, lighting, audio, quality specifications
          - Veo 3 elements verified: cinematic shots, lens specifications, lighting design, color grading, audio design, hyper-realistic quality
          - Economic prompts appropriately simplified for free models
          
          ✅ Backend Integration:
          - /api/images/analyze endpoint working with 30s timeout handling
          - Timeout fallback returns correct structure when Gemini times out
          - Cost estimation working for all models (premium and economic)
          - Video generation request structure correct (tested with economic mode)

  - task: "Prompt sanitization for content policy compliance"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: |
          Sanitization logic updated:
          - Removes facial fidelity instructions (lines 560-610, 367-432)
          - Replaces problematic words (violent, threatening, etc.)
          - Processes all prompts in analysis data recursively
          - Safety net in case Gemini still generates problematic phrases
      - working: true
        agent: "testing"
        comment: |
          SANITIZATION THOROUGHLY TESTED AND VERIFIED:
          
          ✅ Facial Fidelity Removal:
          - Tested with problematic input containing all forbidden terms
          - Input: "Gato ameaçador com olhar violento, preservando 100% da identidade facial original, mantendo alta fidelidade das características faciais..."
          - Output: "Gato olhando para cima. Close-up. Boa iluminação. Movimento natural. Qualidade cinematográfica."
          - ALL problematic content completely removed and replaced with policy-compliant alternatives
          
          ✅ Violent Terms Replacement:
          - "ameaçador" → "impressionante" 
          - "violento" → "intenso"
          - "ataque" → "aproximação"
          - "afiado" → "visível"
          - All replacements working correctly in live testing
          
          ✅ Recursive Sanitization:
          - All prompt fields sanitized: prompt_sora2, prompt_veo3, prompt_economico
          - Cinematic details fields also sanitized: subject_action, camera_work, lighting, audio_design, style
          - No violations found in any generated content across multiple test images
          
          ✅ Safety Net Confirmed:
          - Even if Gemini generates problematic content, sanitization catches and cleans it
          - Backend logs show sanitization working: "✅ Prompt clean" messages
          - No content policy violations reaching video generation APIs

frontend:
  - task: "Display model-specific prompts"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/pages/HomePage.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: |
          Updated HomePage.jsx to handle new prompt structure:
          - Image analysis now sets prompt based on model (sora2 -> prompt_sora2, veo3 -> prompt_veo3)
          - Mode selector (Premium/Economico) updates prompt for recommended model
          - Model selector updates prompt when user changes model manually
          - applyCinematicPrompt() uses model-specific prompts
          - Cinematic details display uses new cinematic_details structure
          - Removed facial_fidelity field display

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 0
  run_ui: false

test_plan:
  current_focus:
    - "Model-specific prompt generation (Sora 2 & Veo 3)"
    - "Prompt sanitization for content policy compliance"
    - "Display model-specific prompts"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: |
      IMPLEMENTATION COMPLETE - Ready for Backend Testing
      
      Changes Made:
      1. Backend (server.py):
         - Updated Gemini system prompt with model-specific templates (Sora 2 vs Veo 3)
         - Added explicit warnings against facial fidelity mentions
         - New JSON structure: prompt_sora2, prompt_veo3, prompt_economico, cinematic_details
         - Maintained aggressive sanitization as safety net
         
      2. Frontend (HomePage.jsx):
         - Updated to use new prompt fields based on selected model
         - Mode selector and model selector update prompts dynamically
         - Cinematic details display updated to new structure
         
      TESTING NEEDED:
      1. Test /api/images/analyze endpoint with various images
      2. Verify Gemini returns correct JSON structure
      3. Confirm prompts are model-specific (different for Sora 2 vs Veo 3)
      4. Ensure NO facial fidelity mentions in generated prompts
      5. Test that sanitization catches any edge cases
      6. Test /api/video/generate with sanitized prompts
      7. Verify no content policy violations from Fal.ai
      
      Key API keys needed: EMERGENT_LLM_KEY, FAL_KEY, ELEVENLABS_KEY, Cloudinary credentials