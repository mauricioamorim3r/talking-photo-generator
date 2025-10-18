#!/usr/bin/env python3
"""
Detailed test to examine model-specific prompt content and structure
"""
import requests
import json

def test_prompt_content():
    """Test and display the actual prompt content for analysis"""
    
    base_url = "https://videofusion-5.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    # Test with a cat image
    test_image_url = "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=400"
    
    print("🔍 DETAILED PROMPT CONTENT ANALYSIS")
    print("=" * 60)
    print(f"Testing with image: {test_image_url}")
    
    try:
        response = requests.post(
            f"{api_url}/images/analyze",
            json={"image_url": test_image_url},
            timeout=35
        )
        
        if response.status_code == 200:
            data = response.json()
            analysis = data.get('analysis', {})
            
            print("\n📋 ANALYSIS RESULTS:")
            print(f"Description: {analysis.get('description', 'N/A')}")
            print(f"Subject Type: {analysis.get('subject_type', 'N/A')}")
            print(f"Premium Model: {analysis.get('recommended_model_premium', 'N/A')}")
            print(f"Economic Model: {analysis.get('recommended_model_economico', 'N/A')}")
            
            print("\n🎬 SORA 2 PROMPT:")
            print("-" * 40)
            sora2_prompt = analysis.get('prompt_sora2', '')
            print(sora2_prompt)
            
            print("\n🎥 VEO 3 PROMPT:")
            print("-" * 40)
            veo3_prompt = analysis.get('prompt_veo3', '')
            print(veo3_prompt)
            
            print("\n💰 ECONOMIC PROMPT:")
            print("-" * 40)
            economic_prompt = analysis.get('prompt_economico', '')
            print(economic_prompt)
            
            print("\n🎭 CINEMATIC DETAILS:")
            print("-" * 40)
            cinematic = analysis.get('cinematic_details', {})
            for key, value in cinematic.items():
                print(f"{key}: {value}")
            
            # Analyze template compliance
            print("\n🔍 TEMPLATE COMPLIANCE ANALYSIS:")
            print("-" * 40)
            
            # Check Sora 2 template elements
            sora2_elements = {
                'physics/movement': any(word in sora2_prompt.lower() for word in ['movimento', 'física', 'natural', 'orgânico']),
                'camera_work': any(word in sora2_prompt.lower() for word in ['câmera', 'plano', 'shot', 'enquadramento']),
                'lighting': any(word in sora2_prompt.lower() for word in ['iluminação', 'luz', 'light']),
                'audio': any(word in sora2_prompt.lower() for word in ['áudio', 'som', 'audio']),
                'quality': any(word in sora2_prompt.lower() for word in ['4k', 'cinematográfico', 'textura'])
            }
            
            print("Sora 2 Template Elements:")
            for element, present in sora2_elements.items():
                status = "✅" if present else "❌"
                print(f"  {status} {element}")
            
            # Check Veo 3 template elements
            veo3_elements = {
                'cinematic_shot': any(word in veo3_prompt.lower() for word in ['cinematic', 'cinematográfico', 'shot']),
                'lens_specs': any(word in veo3_prompt.lower() for word in ['lente', 'mm', 'f/', 'bokeh']),
                'lighting_design': any(word in veo3_prompt.lower() for word in ['lighting', 'iluminação', 'key light', 'fill light']),
                'color_grading': any(word in veo3_prompt.lower() for word in ['color grading', 'tons', 'paleta']),
                'audio_design': any(word in veo3_prompt.lower() for word in ['audio design', 'ambiente sonoro', 'síntese']),
                'hyper_realistic': any(word in veo3_prompt.lower() for word in ['hyper-realistic', 'hiper-realista', '4k'])
            }
            
            print("\nVeo 3 Template Elements:")
            for element, present in veo3_elements.items():
                status = "✅" if present else "❌"
                print(f"  {status} {element}")
            
            # Check for forbidden terms
            print("\n🚨 FORBIDDEN TERMS CHECK:")
            print("-" * 40)
            
            forbidden_terms = [
                'identidade facial', 'fidelidade facial', 'preservar características',
                '100% da identidade', 'expressões faciais devem ser preservadas',
                'alta fidelidade', 'características originais', 'manter identidade'
            ]
            
            all_text = f"{sora2_prompt} {veo3_prompt} {economic_prompt} {json.dumps(cinematic)}"
            
            violations_found = []
            for term in forbidden_terms:
                if term.lower() in all_text.lower():
                    violations_found.append(term)
            
            if violations_found:
                print("🚨 VIOLATIONS FOUND:")
                for violation in violations_found:
                    print(f"  ❌ {violation}")
            else:
                print("✅ No forbidden terms found - Content policy compliant")
            
            # Check prompt differences
            print("\n📊 PROMPT COMPARISON:")
            print("-" * 40)
            print(f"Sora 2 length: {len(sora2_prompt)} characters")
            print(f"Veo 3 length: {len(veo3_prompt)} characters")
            print(f"Economic length: {len(economic_prompt)} characters")
            
            # Calculate similarity (simple word overlap)
            sora2_words = set(sora2_prompt.lower().split())
            veo3_words = set(veo3_prompt.lower().split())
            overlap = len(sora2_words.intersection(veo3_words))
            total_unique = len(sora2_words.union(veo3_words))
            similarity = (overlap / total_unique) * 100 if total_unique > 0 else 0
            
            print(f"Sora 2 vs Veo 3 similarity: {similarity:.1f}%")
            
            if similarity < 70:
                print("✅ Prompts are sufficiently different")
            else:
                print("⚠️ Prompts may be too similar")
            
            return True
            
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_prompt_content()