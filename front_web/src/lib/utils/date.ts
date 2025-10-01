/**
* 날짜 관련 유틸리티 함수
* 날짜 포맷팅, 비교, 계산 등의 기능을 제공합니다.
*/

/**
 * 날짜를 지정된 형식으로 포맷팅
 * @param date - 포맷팅할 날짜 (Date 객체 또는 ISO 문자열, 숫자)
 * @param format - 포맷 문자열 (기본값: 'YYYY-MM-DD')
 *                 'YYYY-MM-DD HH:mm'도 지원
 * @returns 포맷팅된 날짜 문자열
 */
export function formatDate(
  date: Date | string | number | null | undefined,
  format: 'YYYY-MM-DD' | 'YYYY-MM-DD HH:mm' = 'YYYY-MM-DD' // 👈 포맷 옵션 추가
): string {
  if (!date) return '';
  
  const dateObj = new Date(date);
  
  if (isNaN(dateObj.getTime())) {
    console.warn('Invalid date provided to formatDate:', date);
    return '';
  }
  
  const year = dateObj.getFullYear();
  const month = String(dateObj.getMonth() + 1).padStart(2, '0');
  const day = String(dateObj.getDate()).padStart(2, '0');
  
  if (format === 'YYYY-MM-DD HH:mm') {
    const hours = String(dateObj.getHours()).padStart(2, '0');
    const minutes = String(dateObj.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
  }
  
  return `${year}-${month}-${day}`;
}

/**
* 날짜를 YYYY-MM-DD HH:MM 형식으로 포맷팅
* @param date - 포맷팅할 날짜 (Date 객체 또는 ISO 문자열)
* @returns 포맷팅된 날짜 및 시간 문자열
*/
export function formatDateTime(date: Date | string | number | null | undefined): string {
    if (!date) return '';
    
    const dateObj = typeof date === 'object' ? date : new Date(date);
    
    if (isNaN(dateObj.getTime())) {
        console.warn('Invalid date provided to formatDateTime:', date);
        return '';
    }
    
    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    const day = String(dateObj.getDate()).padStart(2, '0');
    const hours = String(dateObj.getHours()).padStart(2, '0');
    const minutes = String(dateObj.getMinutes()).padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}`;
}

/**
* ISO 문자열을 Date 객체로 변환
* @param isoString - ISO 형식의 날짜 문자열
* @returns Date 객체
*/
export function parseISODate(isoString: string | null | undefined): Date | null {
    if (!isoString) return null;

    const date = new Date(isoString);
    return isNaN(date.getTime()) ? null : date;
}

/**
* 백엔드 API 응답의 날짜 문자열을 Date 객체로 변환
* @param dateString - 백엔드에서 받은 날짜 문자열
* @returns Date 객체
*/
export function parseApiDate(dateString: string | null | undefined): Date | null {
    if (!dateString) return null;
    
    // 백엔드 API가 반환하는 날짜 형식에 맞게 처리
    // 예: "2023-05-15T14:30:45" 또는 "2023-05-15 14:30:45"
    const date = new Date(dateString.replace(' ', 'T'));
    return isNaN(date.getTime()) ? null : date;
}

/**
* 상대적 시간 표시 (예: "3분 전", "2시간 전", "어제", "3일 전")
* @param date - 비교할 날짜 (Date 객체 또는 ISO 문자열)
* @returns 상대적 시간 문자열
*/
export function formatRelativeTime(date: Date | string | number | null | undefined): string {
    if (!date) return '';
    
    const dateObj = typeof date === 'object' ? date : new Date(date);
    
    if (isNaN(dateObj.getTime())) {
        console.warn('Invalid date provided to formatRelativeTime:', date);
        return '';
    }
    
    const now = new Date();
    const diffMs = now.getTime() - dateObj.getTime();
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    const diffMonth = Math.floor(diffDay / 30);
    const diffYear = Math.floor(diffMonth / 12);
    
    if (diffSec < 60) {
        return '방금 전';
    } else if (diffMin < 60) {
        return `${diffMin}분 전`;
    } else if (diffHour < 24) {
        return `${diffHour}시간 전`;
    } else if (diffDay === 1) {
        return '어제';
    } else if (diffDay < 30) {
        return `${diffDay}일 전`;
    } else if (diffMonth < 12) {
        return `${diffMonth}개월 전`;
    } else {
        return `${diffYear}년 전`;
    }
}

/**
* 두 날짜 사이의 일수 계산
* @param startDate - 시작 날짜
* @param endDate - 종료 날짜 (기본값: 현재 날짜)
* @returns 두 날짜 사이의 일수
*/
export function daysBetween(
    startDate: Date | string | number,
    endDate: Date | string | number = new Date()
    ): number {
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    // 시간, 분, 초, 밀리초를 0으로 설정하여 날짜만 비교
    start.setHours(0, 0, 0, 0);
    end.setHours(0, 0, 0, 0);
    
    const diffMs = end.getTime() - start.getTime();
    return Math.floor(diffMs / (1000 * 60 * 60 * 24));
}

/**
* 날짜에 일수 추가
* @param date - 기준 날짜
* @param days - 추가할 일수 (음수도 가능)
* @returns 일수가 추가된 새 Date 객체
*/
export function addDays(date: Date | string | number, days: number): Date {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
}

/**
* 날짜가 유효한지 확인
* @param date - 확인할 날짜
* @returns 유효한 날짜인지 여부
*/
export function isValidDate(date: any): boolean {
    if (!date) return false;
    
    const dateObj = typeof date === 'object' ? date : new Date(date);
    return !isNaN(dateObj.getTime());
}

/**
* 두 날짜가 같은 날인지 확인 (시간 무시)
* @param date1 - 첫 번째 날짜
* @param date2 - 두 번째 날짜
* @returns 같은 날인지 여부
*/
export function isSameDay(
    date1: Date | string | number,
    date2: Date | string | number
    ): boolean {
    const d1 = new Date(date1);
    const d2 = new Date(date2);
    
    return (
        d1.getFullYear() === d2.getFullYear() &&
        d1.getMonth() === d2.getMonth() &&
        d1.getDate() === d2.getDate()
    );
}

/**
* 날짜가 오늘인지 확인
* @param date - 확인할 날짜
* @returns 오늘인지 여부
*/
export function isToday(date: Date | string | number): boolean {
    return isSameDay(date, new Date());
}

/**
* 날짜가 과거인지 확인
* @param date - 확인할 날짜
* @returns 과거인지 여부
*/
export function isPast(date: Date | string | number): boolean {
    return new Date(date).getTime() < new Date().setHours(0, 0, 0, 0);
}

/**
* 날짜가 미래인지 확인
* @param date - 확인할 날짜
* @returns 미래인지 여부
*/
export function isFuture(date: Date | string | number): boolean {
    return new Date(date).getTime() > new Date().setHours(23, 59, 59, 999);
}

/**
* 날짜의 시작 시간 (00:00:00)을 반환
* @param date - 기준 날짜
* @returns 해당 날짜의 시작 시간
*/
export function startOfDay(date: Date | string | number): Date {
    const result = new Date(date);
    result.setHours(0, 0, 0, 0);
    return result;
}

/**
* 날짜의 종료 시간 (23:59:59.999)을 반환
* @param date - 기준 날짜
* @returns 해당 날짜의 종료 시간
*/
export function endOfDay(date: Date | string | number): Date {
    const result = new Date(date);
    result.setHours(23, 59, 59, 999);
    return result;
}