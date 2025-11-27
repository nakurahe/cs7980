"""
Quiz Generator using Groq API
Generates educational quizzes from video transcripts and slide data
"""
import json
from groq import Groq
from config import Config

class QuizGenerator:
    def __init__(self, use_baseline=False):
        """
        Initialize the quiz generator with Groq client
        
        Args:
            use_baseline: If True, use baseline API (transcript-only mode)
        """
        Config.validate()
        
        if use_baseline:
            self.client = Groq(api_key=Config.BASELINE_API_KEY)
            self.model = Config.BASELINE_MODEL
            self.mode = "baseline"
        else:
            self.client = Groq(api_key=Config.GROQ_API_KEY)
            self.model = Config.GROQ_MODEL
            self.mode = "multimodal"
    
    def load_json_file(self, file_path):
        """Load and parse a JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in file: {file_path}")
    
    def prepare_multimodal_context(self, transcript_data, slides_data):
        """
        Prepare educational content context from transcript and slides
        
        Args:
            transcript_data: List of transcript segments
            slides_data: Dictionary containing slide information
        
        Returns:
            Formatted context string for the LLM
        """
        context = "# Educational Video Content\n\n"
        
        # Add video metadata
        context += "## Video Information\n"
        context += f"- Total Slides: {slides_data.get('totalSlides', 'Unknown')}\n"
        context += f"- Duration: {slides_data.get('processingTime', 'Unknown')} seconds\n\n"
        
        # Add transcript content
        context += "## Full Transcript\n"
        for segment in transcript_data:
            start_time = self._format_time(segment['start'])
            text = segment['text']
            context += f"[{start_time}] {text}\n"
        
        context += "\n## Slide Content and Topics\n"
        
        # Add slide information
        for slide in slides_data.get('slides', []):
            slide_num = slide.get('imageFile', '').replace('slide_', '').replace('.jpg', '')
            start_time = slide.get('startTime', 'Unknown')
            extracted_text = slide.get('extractedText', 'No text extracted')
            
            context += f"\n### Slide {slide_num} ({start_time})\n"
            context += f"{extracted_text}\n"
        
        return context
    
    def prepare_baseline_context(self, transcript_data):
        """
        Prepare educational content context from transcript only (baseline method)
        
        Args:
            transcript_data: List of transcript segments
        
        Returns:
            Formatted context string for the LLM
        """
        context = "# Educational Video Transcript\n\n"
        
        # Add transcript content with timestamps
        for segment in transcript_data:
            start_time = self._format_time(segment['start'])
            text = segment['text']
            context += f"[{start_time}] {text}\n"
        
        return context
    
    def _format_time(self, seconds):
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def generate_quiz(self, transcript_path, slides_path=None, num_questions=10, difficulty='medium'):
        """
        Generate a quiz based on transcript and optionally slides
        
        Args:
            transcript_path: Path to transcript JSON file
            slides_path: Path to slides JSON file (optional, not used in baseline mode)
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy, medium, hard, mixed)
        
        Returns:
            Dictionary containing the generated quiz
        """
        # Load transcript
        print(f"Loading transcript data from {transcript_path}...")
        transcript_data = self.load_json_file(transcript_path)
        
        # Prepare context based on mode
        if self.mode == "baseline":
            print("Preparing context (BASELINE MODE - transcript only)...")
            context = self.prepare_baseline_context(transcript_data)
            method_description = "transcript-only"
        else:
            if not slides_path:
                raise ValueError("Slides path required for multimodal mode")
            print(f"Loading slides data from {slides_path}...")
            slides_data = self.load_json_file(slides_path)
            print("Preparing context (MULTIMODAL MODE - transcript + slides)...")
            context = self.prepare_multimodal_context(transcript_data, slides_data)
            method_description = "transcript and slides"
        
        # Create prompt for quiz generation
        prompt = self._create_quiz_prompt(context, num_questions, difficulty, method_description)
        
        # Call Groq API
        print(f"Generating {num_questions} quiz questions using {self.model} ({self.mode} mode)...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational content creator specializing in creating high-quality, pedagogically sound quiz questions from educational materials."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        # Parse response
        quiz_json = response.choices[0].message.content
        
        # Extract JSON from response (in case it's wrapped in markdown)
        if "```json" in quiz_json:
            quiz_json = quiz_json.split("```json")[1].split("```")[0].strip()
        elif "```" in quiz_json:
            quiz_json = quiz_json.split("```")[1].split("```")[0].strip()
        
        try:
            quiz_data = json.loads(quiz_json)
            # Add metadata about generation method
            if 'quiz_metadata' in quiz_data:
                quiz_data['quiz_metadata']['generation_mode'] = self.mode
                quiz_data['quiz_metadata']['generation_method'] = method_description
        except json.JSONDecodeError:
            # If JSON parsing fails, wrap the response
            quiz_data = {
                "error": "Failed to parse quiz JSON",
                "raw_response": quiz_json,
                "generation_mode": self.mode
            }
        
        return quiz_data
    
    def _create_quiz_prompt(self, context, num_questions, difficulty, method_description):
        """Create the prompt for quiz generation"""
        prompt = f"""Based on the following educational video content ({method_description}), create a comprehensive quiz with {num_questions} questions.

{context}

Generate a quiz that:
1. Covers the main concepts and topics from the video
2. Has a {difficulty} difficulty level
3. Includes multiple choice questions (4 options each)
4. Provides clear explanations for correct answers
5. References specific timestamps where relevant

Return the quiz in the following JSON format:
{{
  "quiz_metadata": {{
    "title": "Quiz title based on video content",
    "description": "Brief description of what the quiz covers",
    "total_questions": {num_questions},
    "difficulty": "{difficulty}",
    "estimated_time_minutes": <estimated time>
  }},
  "questions": [
    {{
      "question_number": 1,
      "question_text": "The question text",
      "options": [
        {{"id": "A", "text": "Option A"}},
        {{"id": "B", "text": "Option B"}},
        {{"id": "C", "text": "Option C"}},
        {{"id": "D", "text": "Option D"}}
      ],
      "correct_answer": "A",
      "explanation": "Explanation of why this is correct",
      "difficulty": "easy|medium|hard",
      "topic": "Main topic covered",
      "reference": "Timestamp where this is covered"
    }}
  ]
}}

Ensure all questions are clear, unambiguous, and directly related to the video content.
"""
        return prompt
    
    def save_quiz(self, quiz_data, output_path):
        """Save the generated quiz to a JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(quiz_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Quiz saved to: {output_path}")