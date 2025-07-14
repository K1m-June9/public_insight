/**
* 포맷팅 관련 유틸리티 함수
* 숫자, 텍스트 등의 포맷팅 기능을 제공
* 언제든지
* 얼마든지
* 추가가능
*/

/**
* 숫자에 천 단위 구분자(,) 추가
* @param value - 포맷팅할 숫자 또는 숫자 문자열
* @returns 포맷팅된 문자열
*/
export function formatNumber(value: number | string | null | undefined): string {
    if (value === null || value === undefined) return '';
    const num = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(num)) {
        console.warn('Invalid number provided to formatNumber:', value);
        return '';
    }
    return num.toLocaleString('ko-KR');
}

/**
* 파일 크기 포맷팅 (B, KB, MB, GB 단위로 변환)
* @param bytes - 바이트 단위 파일 크기
* @param decimals - 소수점 자릿수 (기본값: 2)
* @returns 포맷팅된 파일 크기 문자열
*/
export function formatFileSize(bytes: number | null | undefined, decimals: number = 2): string {
    if (bytes === null || bytes === undefined || bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`;
}