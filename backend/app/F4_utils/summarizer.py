# import re
# import os
# import fitz #PyMuPDF
# import torch
# from typing import Union, List, Tuple, Optional
# from pathlib import Path
# from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration

# class TextSummarizer:
#     import torch  # PyTorch 임포트 추가

# class TextSummarizer:
#     def __init__(self, model_name: str = 'digit82/kobart-summarization', device: str = 'auto'):
#         """
#         텍스트 요약기 초기화
        
#         Args:
#             model_name (str): 허깅페이스 모델 이름/경로 
#             device (str): 'auto'(기본값), 'cuda', 'cpu' 중 선택
#                          'auto'시 CUDA 가용성 자동 감지
#         """
#         # 디바이스 자동 설정
#         if device == 'auto':
#             self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
#         else:
#             self.device = device.lower()  # 입력 대소문자 통일
            
#         # CUDA 요청했지만 사용 불가능한 경우 경고 출력
#         if self.device.startswith('cuda') and not torch.cuda.is_available():
#             print("⚠️ 경고: CUDA를 사용할 수 없어 CPU로 대체됩니다.")
#             self.device = 'cpu'
            
#         self.model = None
#         self.tokenizer = None
        
#         try:
#             self.tokenizer = PreTrainedTokenizerFast.from_pretrained(model_name)
#             self.model = BartForConditionalGeneration.from_pretrained(model_name)
#             self.model = self.model.to(self.device)  # 선택된 디바이스로 모델 이동
            
#         except Exception as e:
#             raise ModelLoadError(f"모델 로딩 실패: {str(e)}") from e

#     # 이하 기존 메서드들 동일하게 유지...

#     def preprocess(self, text: str) -> str:
#         """
#         텍스트 전처리 수행
        
#         Args:
#             text (str): 원본 텍스트
            
#         Returns:
#             str: 전처리된 텍스트
            
#         Raises:
#             EmptyTextError: 입력 텍스트가 비어 있을 경우
#         """
#         if not text.strip():
#             raise EmptyTextError("전처리 입력 텍스트가 비어 있습니다.")
            
#         text = re.sub(r'\s+', ' ', text)
#         text = re.sub(r'\[.*?\]', '', text)
#         text = re.sub(r'\d+\.\d+', '', text)
#         text = re.sub(r'[●◆▶▼]+', '', text)
#         return text.strip()

#     def chunk_text(self, text: str, sentence_per_chunk: int = 10) -> List[str]:
#         """
#         텍스트를 청크 단위로 분할
        
#         Args:
#             text (str): 입력 텍스트
#             sentence_per_chunk (int): 청크당 문장 수 (기본값: 10)
            
#         Returns:
#             List[str]: 분할된 텍스트 청크 리스트
            
#         Raises:
#             InvalidChunkSizeError: 유효하지 않은 청크 크기 지정시
#         """
#         if sentence_per_chunk < 1:
#             raise InvalidChunkSizeError("청크 크기는 1 이상이어야 합니다.")
            
#         sentences = re.split(r'(?<=[.!?])\s+', text)
#         return [' '.join(sentences[i:i+sentence_per_chunk]).strip() 
#                 for i in range(0, len(sentences), sentence_per_chunk)]

#     def summarize_chunk(self, text: str) -> str:
#         """
#         단일 텍스트 청크 요약
        
#         Args:
#             text (str): 입력 텍스트 청크
            
#         Returns:
#             str: 요약 결과
            
#         Raises:
#             GenerationError: 텍스트 생성 실패시
#         """
#         try:
#             input_ids = self.tokenizer.encode(
#                 text,
#                 return_tensors="pt",
#                 truncation=True,
#                 max_length=1024
#             ).to(self.device)
            
#             summary_ids = self.model.generate(
#                 input_ids,
#                 num_beams=6,
#                 max_length=150,
#                 min_length=80,
#                 repetition_penalty=3.0,
#                 length_penalty=0.8,
#                 early_stopping=True,
#                 no_repeat_ngram_size=4
#             )
#             return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
#         except Exception as e:
#             raise GenerationError(f"텍스트 생성 실패: {str(e)}") from e

#     def hierarchical_summarize(self, text: str, depth: int = 2) -> str:
#         """
#         계층적 요약 수행
        
#         Args:
#             text (str): 입력 텍스트
#             depth (int): 요약 깊이 (기본값: 2)
            
#         Returns:
#             str: 계층적 요약 결과
            
#         Raises:
#             InvalidDepthError: 유효하지 않은 depth 값 입력시
#             RecursionDepthExceeded: 과도한 재귀 깊이 지정시
#         """
#         if depth < 0:
#             raise InvalidDepthError("depth는 0 이상의 정수여야 합니다.")
#         if depth > 5:
#             raise RecursionDepthExceeded("최대 허용 depth(5)를 초과했습니다.")
            
#         if depth == 0:
#             return self.summarize_chunk(text)
            
#         chunks = self.chunk_text(text)
#         summaries = [self.hierarchical_summarize(chunk, depth-1) for chunk in chunks]
#         return self.summarize_chunk(' '.join(summaries))

#     def postprocess(self, summary: str) -> str:
#         """
#         요약 결과 후처리
        
#         Args:
#             summary (str): 원본 요약 텍스트
            
#         Returns:
#             str: 후처리된 최종 요약문
#         """
#         if not summary:
#             return ""
            
#         sentences = list(dict.fromkeys(summary.split('. ')))
#         return '. '.join(sentences).replace(' ,', ',')

#     def extract_pdf(self, file_path: Union[str, Path]) -> str:
#         """
#         PDF 파일에서 텍스트 추출
        
#         Args:
#             file_path (Union[str, Path]): PDF 파일 경로
            
#         Returns:
#             str: 추출된 텍스트
            
#         Raises:
#             FileNotFoundError: 파일이 존재하지 않을 경우
#             InvalidPDFFileError: 유효하지 않은 PDF 파일일 경우
#         """
#         if not os.path.isfile(file_path):
#             raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
            
#         try:
#             doc = fitz.open(file_path)
#             extracted = [page.get_text() for page in doc]
#             return str(extracted).replace('·','\t')
#         except Exception as e:
#             raise InvalidPDFFileError(f"PDF 파싱 실패: {str(e)}") from e

#     def summarize(self, input_data: Union[str, Path], depth: int = 2) -> str:
#         """
#         요약 메인 메서드
        
#         Args:
#             input_data (Union[str, Path]): 입력 텍스트 또는 PDF 파일 경로
#             depth (int): 요약 깊이 (기본값: 2)
            
#         Returns:
#             str: 최종 요약 텍스트
            
#         Raises:
#             InvalidInputError: 유효하지 않은 입력 타입시
#         """
#         if not isinstance(input_data, (str, Path)):
#             raise InvalidInputError("입력은 문자열 또는 파일 경로여야 합니다.")
            
#         try:
#             # 파일 경로인 경우 PDF 추출
#             if isinstance(input_data, (str, Path)) and os.path.isfile(input_data):
#                 if not str(input_data).lower().endswith('.pdf'):
#                     raise InvalidFileTypeError("PDF 파일만 지원합니다.")
#                 raw_text = self.extract_pdf(input_data)
#             else:
#                 raw_text = input_data
                
#             cleaned = self.preprocess(raw_text)
#             summarized = self.hierarchical_summarize(cleaned, depth=depth)
#             return self.postprocess(summarized)
            
#         except Exception as e:
#             raise SummarizationError(f"요약 처리 실패: {str(e)}") from e

# # Custom Exceptions ----------------------------------------------------------
# class TextSummarizerError(Exception):
#     """요약기 기본 예외 클래스"""
#     pass

# class ModelLoadError(TextSummarizerError):
#     """모델 로딩 실패 예외"""
#     pass

# class EmptyTextError(TextSummarizerError):
#     """빈 텍스트 입력 예외"""
#     pass

# class InvalidChunkSizeError(TextSummarizerError):
#     """잘못된 청크 크기 예외"""
#     pass

# class GenerationError(TextSummarizerError):
#     """텍스트 생성 실패 예외"""
#     pass

# class InvalidDepthError(TextSummarizerError):
#     """잘못된 depth 값 예외"""
#     pass

# class RecursionDepthExceeded(TextSummarizerError):
#     """과도한 재귀 깊이 예외"""
#     pass

# class InvalidPDFFileError(TextSummarizerError):
#     """잘못된 PDF 파일 예외"""
#     pass

# class InvalidInputError(TextSummarizerError):
#     """잘못된 입력 타입 예외"""
#     pass

# class InvalidFileTypeError(TextSummarizerError):
#     """지원하지 않는 파일 타입 예외"""
#     pass

# class SummarizationError(TextSummarizerError):
#     """일반 요약 오류 예외"""
#     pass