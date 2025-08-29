/**
 * Utility functions for JSON detection and handling
 */

/**
 * Checks if a string content appears to be JSON
 * @param content - The string content to check
 * @returns true if the content appears to be JSON, false otherwise
 */
export function isJsonContent(content: string): boolean {
  if (!content || typeof content !== 'string') {
    return false;
  }
  
  const trimmed = content.trim();
  
  // Quick checks for common JSON patterns
  if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
    try {
      JSON.parse(trimmed);
      return true;
    } catch {
      // Might be malformed JSON, but still looks like JSON
      return true;
    }
  }
  
  if (trimmed.startsWith('[') && trimmed.endsWith(']')) {
    try {
      JSON.parse(trimmed);
      return true;
    } catch {
      // Might be malformed JSON, but still looks like JSON
      return true;
    }
  }
  
  // Check if it's a JSON string (quoted string)
  if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
    try {
      JSON.parse(trimmed);
      return true;
    } catch {
      // Might be malformed JSON string, but still looks like JSON
      return true;
    }
  }
  
  // Try to parse as JSON (for cases where content might be partial)
  try {
    JSON.parse(trimmed);
    return true;
  } catch {
    // Not valid JSON
    return false;
  }
}

/**
 * Safely parses JSON content, returns null if parsing fails
 * @param content - The string content to parse
 * @returns Parsed JSON object or null if parsing fails
 */
export function safeJsonParse(content: string): any | null {
  try {
    return JSON.parse(content);
  } catch {
    return null;
  }
}
