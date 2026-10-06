import { API_URL } from '../config';

const BOOKS_URL = `${API_URL}/books`;

const getHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
};

const fetchWithAuth = async (url, options = {}) => {
  const response = await fetch(url, {
    ...options,
    headers: {
      ...getHeaders(),
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorData = null;
    try {
      errorData = await response.json();
    } catch (e) {
      const error = new Error(`Error ${response.status}: Failed to fetch data`);
      error.status = response.status;
      throw error;
    }

    // FastAPI returns detailed error information in the 'detail' field
    const error = new Error(errorData.detail || 'API request failed');
    error.status = response.status;
    throw error;
  }

  // Handle 204 No Content responses which lack a JSON body to parse
  if (response.status === 204) {
    return null;
  }

  return response.json();
};

export const bookService = {
  async getBooks(filters = {}) {
    const queryParams = new URLSearchParams();
    if (filters.status) queryParams.append('status', filters.status);
    if (filters.search) queryParams.append('search', filters.search);

    // Append query parameters only if filters are explicitly provided
    const url = queryParams.toString() ? `${BOOKS_URL}?${queryParams.toString()}` : BOOKS_URL;
    return fetchWithAuth(url);
  },

  async getBookStats() {
    return fetchWithAuth(`${BOOKS_URL}/stats`);
  },

  async createBook(bookData) {
    return fetchWithAuth(BOOKS_URL, {
      method: 'POST',
      body: JSON.stringify(bookData),
    });
  },

  async getBookById(id) {
    return fetchWithAuth(`${BOOKS_URL}/${id}`);
  },

  async updateBook(id, updateData) {
    return fetchWithAuth(`${BOOKS_URL}/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
  },

  async deleteBook(id) {
    return fetchWithAuth(`${BOOKS_URL}/${id}`, {
      method: 'DELETE',
    });
  },

  async getPublicBooks(filters = {}, options = {}) {
    const queryParams = new URLSearchParams();
    if (filters.genre) queryParams.append('genre', filters.genre);
    if (filters.search) queryParams.append('search', filters.search);

    const url = queryParams.toString()
      ? `${BOOKS_URL}/public?${queryParams.toString()}`
      : `${BOOKS_URL}/public`;

    return fetchWithAuth(url, options);
  },

  async getPublicBookById(id, options = {}) {
    return fetchWithAuth(`${BOOKS_URL}/public/${id}`, options);
  },

  async getPublicBookRecommendations(id, limit = 5, options = {}) {
    const safeLimit = Math.min(Math.max(Number(limit) || 5, 1), 5);
    const bookId = encodeURIComponent(id);

    return fetchWithAuth(
      `${BOOKS_URL}/public/${bookId}/recommendations?limit=${safeLimit}`,
      options,
    );
  },

  async getRecommendationsForMe(limit = 5, options = {}) {
    const safeLimit = Math.min(Math.max(Number(limit) || 5, 1), 5);
    return fetchWithAuth(
      `${BOOKS_URL}/recommendations/for-me?limit=${safeLimit}`,
      options,
    );
  },

  async getSharedBook(shareToken, options = {}) {
    return fetchWithAuth(`${BOOKS_URL}/shared/${encodeURIComponent(shareToken)}`, options);
  },

  async startReadingPublicBook(bookId, shareToken = null) {
    const query = shareToken
      ? `?share_token=${encodeURIComponent(shareToken)}`
      : '';
    return fetchWithAuth(`${BOOKS_URL}/public/${encodeURIComponent(bookId)}/reading-progress${query}`, {
      method: 'POST',
    });
  },

  async updatePublicBookProgress(bookId, progressData, shareToken = null) {
    const query = shareToken
      ? `?share_token=${encodeURIComponent(shareToken)}`
      : '';
    return fetchWithAuth(`${BOOKS_URL}/public/${encodeURIComponent(bookId)}/reading-progress${query}`, {
      method: 'PUT',
      body: JSON.stringify(progressData),
    });
  },

  async getReadingHistory(bookId) {
    return fetchWithAuth(`${BOOKS_URL}/${bookId}/reading-history`);
  },

  async deleteReadingHistoryEntry(bookId, historyId) {
    return fetchWithAuth(`${BOOKS_URL}/${bookId}/reading-history/${historyId}`, {
      method: 'DELETE',
    });
  },

  async deleteAllReadingHistory(bookId) {
    return fetchWithAuth(`${BOOKS_URL}/${bookId}/reading-history`, {
      method: 'DELETE',
    });
  },

};
