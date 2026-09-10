/**
 * Nexus API Client
 * Enforces typed API requests, authentication header injection, and standardized error extraction.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export class ApiError extends Error {
  code: string;
  status: number;

  constructor(message: string, code: string = "UNKNOWN_ERROR", status: number = 500) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
  }
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("nexus_token") : null;

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const url = endpoint.startsWith("http") ? endpoint : `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorData: any = {};
    try {
      errorData = await response.json();
    } catch {
      // Non-JSON response
    }
    const message = errorData?.error?.message || errorData?.detail || response.statusText || "Request failed";
    const code = errorData?.error?.code || `HTTP_${response.status}`;
    throw new ApiError(message, code, response.status);
  }

  // Support 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}
