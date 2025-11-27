"""
Main entry point for the Quiz Generator application
Generates both multimodal (transcript + slides) and baseline (transcript only) quizzes
"""
import os
import argparse
from quiz_generator import QuizGenerator
from config import Config

def generate_all_quizzes(num_videos=10, start_index=0, num_questions=10, difficulty='medium'):
    """
    Generate all quizzes for multiple videos
    
    Args:
        num_videos: Number of video datasets to process (default: 10)
        start_index: Starting video index (default: 0)
        num_questions: Number of questions per quiz
        difficulty: Difficulty level
    """
    # Create output directory if it doesn't exist
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    
    print("="*70)
    print("Educational Video Quiz Generator - Batch Processing")
    print("="*70)
    print(f"\nConfiguration:")
    print(f"  - Processing videos: {start_index} to {start_index + num_videos - 1}")
    print(f"  - Total videos: {num_videos}")
    print(f"  - Questions per quiz: {num_questions}")
    print(f"  - Difficulty: {difficulty}")
    print(f"  - Output directory: {Config.OUTPUT_DIR}")
    print("\n" + "="*70)
    
    # Statistics
    multimodal_success = 0
    multimodal_failed = 0
    baseline_success = 0
    baseline_failed = 0
    
    # Process each video
    for i in range(start_index, start_index + num_videos):
        video_num = i - start_index + 1
        print(f"\n{'='*70}")
        print(f"Processing Video {i} ({video_num}/{num_videos})")
        print("="*70)
        
        # Define file paths
        transcript_path = os.path.join(Config.DATA_DIR, f'transcript{i}.json')
        slides_path = os.path.join(Config.DATA_DIR, f'slides{i}.json')
        multimodal_output = os.path.join(Config.OUTPUT_DIR, f'quiz{i}.json')
        baseline_output = os.path.join(Config.OUTPUT_DIR, f'baseline{i}.json')
        
        # Check if files exist
        if not os.path.exists(transcript_path):
            print(f"Warning: {transcript_path} not found. Skipping video {i}.")
            multimodal_failed += 1
            baseline_failed += 1
            continue
        
        # Generate multimodal quiz (transcript + slides)
        print(f"\n--- Multimodal Quiz Generation (quiz{i}.json) ---")
        try:
            if not os.path.exists(slides_path):
                print(f" Warning: {slides_path} not found. Skipping multimodal quiz for video {i}.")
                multimodal_failed += 1
            else:
                multimodal_generator = QuizGenerator(use_baseline=False)
                multimodal_quiz = multimodal_generator.generate_quiz(
                    transcript_path=transcript_path,
                    slides_path=slides_path,
                    num_questions=num_questions,
                    difficulty=difficulty
                )
                multimodal_generator.save_quiz(multimodal_quiz, multimodal_output)
                multimodal_success += 1
        except Exception as e:
            print(f" Error generating multimodal quiz for video {i}: {e}")
            multimodal_failed += 1
        
        # Generate baseline quiz (transcript only)
        print(f"\n--- Baseline Quiz Generation (baseline{i}.json) ---")
        try:
            baseline_generator = QuizGenerator(use_baseline=True)
            baseline_quiz = baseline_generator.generate_quiz(
                transcript_path=transcript_path,
                slides_path=None,  # Not used in baseline mode
                num_questions=num_questions,
                difficulty=difficulty
            )
            baseline_generator.save_quiz(baseline_quiz, baseline_output)
            baseline_success += 1
        except Exception as e:
            print(f" Error generating baseline quiz for video {i}: {e}")
            baseline_failed += 1
    
    # Print summary
    print("\n" + "="*70)
    print("Generation Complete - Summary")
    print("="*70)
    print(f"\nMultimodal Quizzes (transcript + slides):")
    print(f"  ✓ Success: {multimodal_success}")
    print(f"  ✗ Failed:  {multimodal_failed}")
    print(f"\nBaseline Quizzes (transcript only):")
    print(f"  ✓ Success: {baseline_success}")
    print(f"  ✗ Failed:  {baseline_failed}")
    print(f"\nTotal quizzes generated: {multimodal_success + baseline_success}")
    print(f"Output location: {Config.OUTPUT_DIR}/")
    print("="*70)

def generate_single_quiz(transcript_path, slides_path, output_path, 
                        num_questions, difficulty, baseline=False):
    """Generate a single quiz"""
    try:
        generator = QuizGenerator(use_baseline=baseline)
        
        quiz_data = generator.generate_quiz(
            transcript_path=transcript_path,
            slides_path=slides_path if not baseline else None,
            num_questions=num_questions,
            difficulty=difficulty
        )
        
        generator.save_quiz(quiz_data, output_path)
        
        print("\n" + "="*70)
        print("Quiz generation completed successfully!")
        print("="*70)
        
        if 'quiz_metadata' in quiz_data:
            print(f"\nQuiz Title: {quiz_data['quiz_metadata'].get('title', 'N/A')}")
            print(f"Questions: {quiz_data['quiz_metadata'].get('total_questions', 'N/A')}")
            print(f"Difficulty: {quiz_data['quiz_metadata'].get('difficulty', 'N/A')}")
            print(f"Mode: {quiz_data['quiz_metadata'].get('generation_mode', 'N/A')}")
        
        print(f"\nOutput file: {output_path}")
        
    except FileNotFoundError as e:
        print(f"\n Error: {e}")
        print("\nMake sure your input files exist:")
        print(f"  - Transcript: {transcript_path}")
        if not baseline:
            print(f"  - Slides: {slides_path}")
    except ValueError as e:
        print(f"\n Configuration Error: {e}")
    except Exception as e:
        print(f"\n Unexpected Error: {e}")
        print("\nPlease check your input files and API configuration.")

def main():
    """Main function to run the quiz generator"""
    
    parser = argparse.ArgumentParser(
        description='Generate educational quizzes from video transcripts and slides'
    )
    
    # Mode selection
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Generate all quizzes (quiz0-9 and baseline0-9) from data folder'
    )
    parser.add_argument(
        '--num-videos',
        type=int,
        default=10,
        help='Number of videos to process in batch mode (default: 10)'
    )
    parser.add_argument(
        '--start-index',
        type=int,
        default=0,
        help='Starting video index for batch mode (default: 0)'
    )
    
    # Single quiz mode arguments
    parser.add_argument(
        '--transcript',
        type=str,
        help='Path to transcript JSON file'
    )
    parser.add_argument(
        '--slides',
        type=str,
        help='Path to slides JSON file'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output path for generated quiz'
    )
    parser.add_argument(
        '--baseline',
        action='store_true',
        help='Use baseline mode (transcript only)'
    )
    
    # Quiz configuration
    parser.add_argument(
        '--questions',
        type=int,
        default=10,
        help='Number of questions to generate (default: 10)'
    )
    parser.add_argument(
        '--difficulty',
        type=str,
        choices=['easy', 'medium', 'hard', 'mixed'],
        default='medium',
        help='Difficulty level (default: medium)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.batch:
            # Batch mode - generate all quizzes
            generate_all_quizzes(
                num_videos=args.num_videos,
                start_index=args.start_index,
                num_questions=args.questions,
                difficulty=args.difficulty
            )
        else:
            # Single quiz mode
            if not args.transcript:
                print("Error: --transcript is required for single quiz mode")
                print("Use --batch for batch processing or --help for more information")
                return
            
            if not args.baseline and not args.slides:
                print("Error: --slides is required for multimodal mode")
                print("Use --baseline flag for transcript-only generation")
                return
            
            if not args.output:
                args.output = os.path.join(
                    Config.OUTPUT_DIR, 
                    'baseline_quiz.json' if args.baseline else 'multimodal_quiz.json'
                )
            
            os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
            
            generate_single_quiz(
                transcript_path=args.transcript,
                slides_path=args.slides,
                output_path=args.output,
                num_questions=args.questions,
                difficulty=args.difficulty,
                baseline=args.baseline
            )
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n Fatal Error: {e}")

if __name__ == "__main__":
    main()