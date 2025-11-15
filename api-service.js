/**
 * API Service for Palefò
 * Handles communication with the backend API
 */

// Add import for the CORS proxy
import corsProxy from "./cors-proxy.js";

// API Configuration
const API_BASE_URLS = {
  local: "https://localhost:7152/api",
  development: 'https://localhost:7152/api',
    production: 'https://palefo-mock-api-92d4b6d1e5b9.herokuapp.com/api'. // mocked palefo api
  //production: "https://palefo-gxh3b3dpd6e4e0fh.westus-01.azurewebsites.net/api"
  //production: "http://localhost:5297/api"//"https://palefo-gxh3b3dpd6e4e0fh.westus-01.azurewebsites.net/api"
};

// Determine which environment to use
// Check if running locally
const isLocalhost = window.location.hostname === 'localhost' || 
                   window.location.hostname === '127.0.0.1' || 
                   window.location.hostname === '[::1]';

// Use development URL for local testing
//const ENVIRONMENT = isLocalhost ? "development" : "production";
const ENVIRONMENT = "production";

// Set the current API URL based on environment
let API_BASE_URL = API_BASE_URLS[ENVIRONMENT];

// Flag to track if we've switched to fallback URL
let usingFallbackUrl = false;

// Note: In development, you might see SSL errors when connecting to a local HTTPS server
// with a self-signed certificate. To fix this, we're using the HTTP endpoint directly.

// Loading indicator functions
function showLoading() {
  document.body.classList.add("loading-active");
}

function hideLoading() {
  document.body.classList.remove("loading-active");
}

// Helper function to get the current API URL
function getApiUrl() {
  return usingFallbackUrl ? API_BASE_URLS.local : API_BASE_URL;
}

// Helper function to get a proxy URL for Azure blob URLs
function getProxiedUrl(url) {
  // If it's an Azure blob URL, proxy it through our server
  if (url && url.includes("blob.core.windows.net")) {
    return `${getApiUrl()}/api/proxy-audio?url=${encodeURIComponent(url)}`;
  }
  return url;
}

// Helper to handle CORS errors
async function fetchWithCorsHandling(url, options = {}) {
  try {
    // Ensure proper CORS settings are applied
    const corsOptions = {
      ...options,
      mode: "cors",
      credentials: "include",
      headers: {
        ...(options.headers || {}),
        Accept: "application/json",
      },
    };

    const response = await fetch(url, corsOptions);
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("API request error:", error);

    // Handle CORS errors specifically
    if (error.message.includes("has been blocked by CORS policy")) {
      console.warn(
        "CORS error detected. Consider using a CORS proxy or updating backend CORS settings."
      );

      // Show a user-friendly error message
      const toastContainer = document.querySelector(".toast-container");
      if (toastContainer) {
        const toast = document.createElement("div");
        toast.className = "toast toast-error";
        toast.innerHTML = `
                    <div class="toast-content">
                        <strong>Connection Error</strong>
                        <p>Unable to connect to the API due to CORS restrictions. Please check your network settings or try again later.</p>
                    </div>
                    <button class="toast-close">&times;</button>
                `;
        toastContainer.appendChild(toast);

        // Add event listener to close button
        toast.querySelector(".toast-close").addEventListener("click", () => {
          toast.remove();
        });

        // Auto remove after 5 seconds
        setTimeout(() => {
          toast.remove();
        }, 5000);
      }
    }

    throw error;
  }
}

// API Service object
const ApiService = {
  // Get the current API URL
  getApiUrl() {
    return getApiUrl();
  },

  // Manual override for API URL
  setApiUrl(url) {
    if (url && url.trim() !== "") {
      localStorage.setItem("palefo-api-url", url.trim());
      return true;
    }
    return false;
  },

  /**
   * Get random sentences from the API
   * @param {number} count - Number of sentences to retrieve
   * @param {Array<number>} excludeIds - Optional array of sentence IDs to exclude
   * @returns {Promise<Array>} Array of sentence objects
   */
  async getRandomSentences(count = 1, excludeIds = null) {
    showLoading();
    try {
      let url = `${getApiUrl()}/sentences/random?count=${count}`;

      // Add excludeIds if provided
      if (excludeIds && excludeIds.length > 0) {
        url += `&excludeIds=${excludeIds.join(",")}`;
      }

      // Use fetchWithCorsHandling to ensure consistent CORS handling
      return await fetchWithCorsHandling(url);
    } catch (error) {
      console.error("Error fetching random sentences:", error);
      throw error;
    } finally {
      hideLoading();
    }
  },

  /**
   * Get sentences by category
   * @param {string} category - Category name
   * @param {number} count - Number of sentences to retrieve
   * @returns {Promise<Array>} Array of sentence objects
   */
  async getSentencesByCategory(category, count = 1) {
    showLoading();
    try {
      const response = await fetch(
        `${getApiUrl()}/sentences/category/${encodeURIComponent(
          category
        )}?count=${count}`
      );

      if (!response.ok) {
        throw new Error(
          `Error fetching sentences by category: ${response.status}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error("Error fetching sentences by category:", error);
      throw error;
    } finally {
      hideLoading();
    }
  },

  /**
   * Get sentences by category using simple query (no stored procedure)
   * @param {string} category - Category name
   * @param {number} count - Number of sentences to retrieve
   * @returns {Promise<Array>} Array of sentence objects
   */
  async getSentencesByCategorySimple(category, count = 1) {
    showLoading();
    try {
      const response = await fetch(
        `${getApiUrl()}/sentences/category-simple/${encodeURIComponent(
          category
        )}?count=${count}`
      );

      if (!response.ok) {
        throw new Error(
          `Error fetching sentences by category: ${response.status}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error("Error fetching sentences by category (simple):", error);
      throw error;
    } finally {
      hideLoading();
    }
  },

  /**
   * Get sentences by difficulty level
   * @param {number} level - Difficulty level (1-5)
   * @param {number} count - Number of sentences to retrieve
   * @returns {Promise<Array>} Array of sentence objects
   */
  async getSentencesByDifficulty(level, count = 1) {
    showLoading();
    try {
      const response = await fetch(
        `${getApiUrl()}/sentences/difficulty/${level}?count=${count}`
      );

      if (!response.ok) {
        throw new Error(
          `Error fetching sentences by difficulty: ${response.status}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error("Error fetching sentences by difficulty:", error);
      throw error;
    } finally {
      hideLoading();
    }
  },

  /**
   * Fetch statistics from the API
   * @returns {Promise<Object>} Statistics object with totalContributions, uniqueContributors, totalAudioHours
   */
  async getStatistics() {
    showLoading();
    try {
      const options = {
        method: "GET",
        mode: "cors",
        credentials: "include",
        headers: {
          Accept: "application/json",
        },
      };

      // Use CORS proxy if enabled
      let response;
      if (corsProxy.isEnabled()) {
        response = await corsProxy.fetch(`${getApiUrl()}/statistics`, options);
      } else {
        response = await fetch(`${getApiUrl()}/statistics`, options);
      }

      if (!response.ok) {
        throw new Error(
          `Error fetching statistics: ${response.status} ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error("Error fetching statistics:", error);
      throw error;
    } finally {
      hideLoading();
    }
  },

  /**
   * Fetch top contributors from the API
   * @param {number} limit - Number of top contributors to fetch (default: 10)
   * @returns {Promise<Array>} Array of top contributor objects
   */
  async getTopContributors(limit = 10) {
    showLoading();
    console.log(
      `Fetching top contributors from: ${getApiUrl()}/contributors/top?limit=${limit}`
    );

    try {
      const response = await fetch(
        `${getApiUrl()}/contributors/top?limit=${limit}`
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`API error (${response.status}): ${errorText}`);
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const contributors = await response.json();
      console.log(
        `Retrieved ${
          contributors ? contributors.length : 0
        } top contributors from API`
      );
      return contributors;
    } catch (error) {
      console.error("Error fetching top contributors:", error);
      throw error;
    } finally {
      hideLoading();
    }
  },

  /**
   * Submit a new contribution with text and audio
   * @param {string} KreyòlText - The Haitian Kreyòl text
   * @param {Blob} audioBlob - The recorded audio as a Blob
   * @param {string} email - Optional contributor email (defaults to empty string)
   * @param {string} gender - Optional gender selection (defaults to empty string)
   * @param {string} region - Optional region selection (defaults to empty string)
   * @returns {Promise<Object>} The created contribution object
   */
  async submitContribution(
    KreyòlText,
    audioBlob,
    email = "",
    gender = "",
    region = ""
  ) {
    showLoading();
    try {
      // Validate audioBlob before proceeding
      if (!audioBlob || audioBlob.size === 0) {
        throw new Error(
          "Invalid audio recording: The audio blob is empty or undefined."
        );
      }

      // Determine the correct file extension based on MIME type
      let fileExtension = "wav";
      if (audioBlob.type) {
        if (audioBlob.type.includes("mpeg") || audioBlob.type.includes("mp3")) {
          fileExtension = "mp3";
        } else if (audioBlob.type.includes("webm")) {
          fileExtension = "webm";
        }
      }

      console.log(
        `Submitting audio with MIME type: ${audioBlob.type}, using extension: ${fileExtension}`
      );

      const formData = new FormData();
      formData.append("KreyòlText", KreyòlText);
      formData.append("AudioFile", audioBlob, `recording.${fileExtension}`);

      // Only add email if it's provided
      if (email) {
        formData.append("Email", email);
      }

      // Add gender if provided
      if (gender) {
        formData.append("Gender", gender);
      }

      // Add region if provided
      if (region) {
        formData.append("Region", region);
      }

      console.log(`Submitting to API endpoint: ${getApiUrl()}/contributions`);

      const response = await fetchWithCorsHandling(`${getApiUrl()}/contributions`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`API error (${response.status}): ${errorText}`);
        throw new Error(
          `API error: ${response.status} - ${errorText || response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error("Error submitting contribution:", error);

      // Handle CORS errors
      if (error.message.includes("has been blocked by CORS policy")) {
        console.warn("CORS error detected when submitting contribution.");
      }

      throw error;
    } finally {
      hideLoading();
    }
  },

  /**
   * Get a list of contributions
   * @param {number} page - Page number (starting from 1)
   * @param {number} pageSize - Number of items per page
   * @returns {Promise<Array>} Array of contribution objects
   */
  async getContributions(page = 1, pageSize = 20, includeUnapproved = false) {
    showLoading();
    try {
      const url = new URL(`${getApiUrl()}/contributions`);
      url.searchParams.append("page", page);
      url.searchParams.append("pageSize", pageSize);
      if (includeUnapproved) {
        url.searchParams.append("includeUnapproved", "true");
      }

      const data = await fetchWithCorsHandling(url.toString());

      // Process each contribution to proxy Azure blob URLs if needed
      if (data && data.items) {
        data.items = data.items.map((contribution) => {
          if (contribution.audioUrl) {
            contribution.audioUrl = getProxiedUrl(contribution.audioUrl);
          }
          return contribution;
        });
      }

      return data;
    } catch (error) {
      console.error("Error fetching contributions:", error);

      // Try fallback URL if not already using it
      if (!usingFallbackUrl && error.message.includes("API error")) {
        console.log("Switching to fallback URL");
        usingFallbackUrl = true;
        return this.getContributions(page, pageSize);
      }

      throw error;
    } finally {
      hideLoading();
    }
  },

  /**
   * Get a specific contribution by ID
   * @param {number} id - Contribution ID
   * @returns {Promise<Object>} Contribution object
   */
  async getContributionById(id) {
    showLoading();
    try {
      return await fetchWithCorsHandling(`${getApiUrl()}/contributions/${id}`);
    } catch (error) {
      console.error(`Error fetching contribution with ID ${id}:`, error);
      throw error;
    } finally {
      hideLoading();
    }
  },

  /**
   * Check if a user is eligible for prizes based on their contribution count
   * @param {string} email - User's email address
   * @returns {Promise<Object>} Object containing prize eligibility
   */
  async checkPrizeEligibility(email) {
    try {
      if (!email) {
        return {
          eligible: false,
          message: "Email required for prize eligibility",
          contributionCount: 0,
          laptopEligible: false,
          tshirtEligible: false,
        };
      }

      // In a real implementation, this would call a dedicated API endpoint
      // For now, we'll use the top contributors to determine eligibility
      const contributors = await this.getTopContributors(50);
      const userContribution = contributors.find((c) => c.email === email);

      if (!userContribution) {
        return {
          eligible: false,
          message: "No contributions found for this email",
          contributionCount: 0,
          laptopEligible: false,
          tshirtEligible: false,
        };
      }

      const contributionCount = userContribution.contributionCount || 0;
      const laptopEligible = contributionCount >= 10000;
      const tshirtEligible = contributionCount >= 1000;

      return {
        eligible: tshirtEligible,
        message: laptopEligible
          ? "Congratulations! You've qualified for a laptop!"
          : tshirtEligible
          ? "You've qualified for a t-shirt and surprise gift!"
          : `You need ${
              1000 - contributionCount
            } more valid contributions to qualify for a t-shirt`,
        contributionCount,
        laptopEligible,
        tshirtEligible,
      };
    } catch (error) {
      console.error("Error checking prize eligibility:", error);
      throw error;
    }
  },

  /**
   * Admin authentication (simple implementation for demo purposes)
   * In a production environment, use proper authentication with JWT or similar
   * @param {string} username - Admin username
   * @param {string} password - Admin password
   * @returns {Promise<boolean>} Authentication result
   */
  async authenticateAdmin(username, password) {
    // Note: In a real app, this would call a backend authentication endpoint
    // For demo purposes, we're using hard-coded credentials
    if (username === "admin" && password === "palefo2023") {
      // Store authentication state in localStorage
      localStorage.setItem("adminAuthenticated", "true");
      return true;
    }
    return false;
  },

  /**
   * Check if user is authenticated as admin
   * @returns {boolean} Authentication status
   */
  isAdminAuthenticated() {
    return localStorage.getItem("adminAuthenticated") === "true";
  },

  /**
   * Log out admin
   */
  logoutAdmin() {
    localStorage.removeItem("adminAuthenticated");
  },

  /**
   * Debug function to test API connectivity
   * @returns {Promise<Object>} Debug information
   */
  async testApiConnection() {
    try {
      console.log("Testing API connection...");
      const currentUrl = getApiUrl();
      console.log(`Current API URL: ${currentUrl}`);

      // Test statistics endpoint
      console.log("Testing statistics endpoint...");
      const statsResponse = await fetch(`${currentUrl}/statistics`);
      const statsStatus = statsResponse.status;
      const statsData = statsResponse.ok
        ? await statsResponse.json()
        : "Failed";

      // Test contributions endpoint
      console.log("Testing contributions endpoint...");
      const contribResponse = await fetch(
        `${currentUrl}/contributions?page=1&pageSize=5`
      );
      const contribStatus = contribResponse.status;
      const contribData = contribResponse.ok
        ? await contribResponse.json()
        : "Failed";

      // Test sentences endpoint
      console.log("Testing sentences endpoint...");
      const sentencesResponse = await fetch(
        `${currentUrl}/sentences/random?count=3`
      );
      const sentencesStatus = sentencesResponse.status;
      const sentencesData = sentencesResponse.ok
        ? await sentencesResponse.json()
        : "Failed";

      // Test Gemini endpoint
      console.log("Testing Gemini endpoint...");
      let geminiStatus = 0;
      let geminiData = "Not tested";
      try {
        const geminiResponse = await fetch(
          `${currentUrl}/ai/gemini-phrase?difficultyLevel=2`
        );
        geminiStatus = geminiResponse.status;
        geminiData = geminiResponse.ok ? await geminiResponse.json() : "Failed";
      } catch (error) {
        console.warn("Gemini endpoint test failed:", error);
        geminiStatus = 500;
        geminiData = "Error: " + error.message;
      }

      return {
        apiUrl: currentUrl,
        statistics: {
          status: statsStatus,
          data: statsData,
        },
        contributions: {
          status: contribStatus,
          data: contribData,
        },
        sentences: {
          status: sentencesStatus,
          data: sentencesData,
        },
        gemini: {
          status: geminiStatus,
          data: geminiData,
        },
      };
    } catch (error) {
      console.error("Error testing API connection:", error);
      return {
        error: error.message,
        stack: error.stack,
      };
    }
  },

  /**
   * Get contributions for admin moderation
   * @param {number} page - Page number
   * @param {number} pageSize - Items per page
   * @param {string} filter - Filter by status: 'pending', 'approved', or 'rejected'
   * @returns {Promise<Object>} Contributions with pagination info
   */
  async getContributionsForModeration(
    page = 1,
    pageSize = 10,
    filter = "pending"
  ) {
    showLoading();
    try {
      // Build query parameters based on filter
      let queryParams = `page=${page}&pageSize=${pageSize}&includeUnapproved=true`;

      const contributions = await fetchWithCorsHandling(
        `${getApiUrl()}/contributions?${queryParams}`
      );

      // Filter results on the client side based on the filter parameter
      let filteredContributions;
      switch (filter) {
        case "approved":
          filteredContributions = contributions.filter((c) => c.isApproved);
          break;
        case "rejected":
          filteredContributions = contributions.filter(
            (c) => !c.isApproved && c.rejectionReason
          );
          break;
        case "pending":
        default:
          filteredContributions = contributions.filter(
            (c) => !c.isApproved && !c.rejectionReason
          );
          break;
      }

      return {
        items: filteredContributions,
        page,
        pageSize,
        filter,
      };
    } catch (error) {
      console.error("Error fetching contributions for moderation:", error);
      throw error;
    } finally {
      hideLoading();
    }
  },

  /**
   * Approve or reject a contribution
   * @param {number} id - Contribution ID
   * @param {boolean} approved - Whether to approve or reject
   * @param {string|null} rejectionReason - Reason for rejection (required if rejecting)
   * @returns {Promise<Object>} Updated contribution
   */
  async moderateContribution(id, approved, rejectionReason = null) {
    showLoading();
    try {
      if (!approved && !rejectionReason) {
        throw new Error(
          "Rejection reason is required when rejecting a contribution"
        );
      }

      const response = await fetch(
        `${getApiUrl()}/contributions/${id}/approval`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            approved,
            rejectionReason,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Error moderating contribution with ID ${id}:`, error);

      // Handle CORS errors
      if (error.message.includes("has been blocked by CORS policy")) {
        console.warn("CORS error detected during moderation action.");
      }

      throw error;
    } finally {
      hideLoading();
    }
  },

  /**
   * Get AI-generated random Haitian Kreyòl phrase
   * @param {Object} options - Optional parameters
   * @param {string} options.category - Optional category for the phrase
   * @param {number} options.difficultyLevel - Optional difficulty level (1-5)
   * @param {number} options.minWords - Optional minimum word count
   * @param {number} options.maxWords - Optional maximum word count
   * @returns {Promise<Object>} Object containing the generated phrase and metadata
   */
  async getAIGeneratedPhrase(options = {}) {
    showLoading();
    try {
      // Build the query parameters
      const queryParams = new URLSearchParams();

      if (options.category) {
        queryParams.append("category", options.category);
      }

      if (options.difficultyLevel !== undefined) {
        queryParams.append("difficultyLevel", options.difficultyLevel);
      }

      if (options.minWords !== undefined) {
        queryParams.append("minWords", options.minWords);
      }

      if (options.maxWords !== undefined) {
        queryParams.append("maxWords", options.maxWords);
      }

      // Build the URL with query parameters
      let url = `${getApiUrl()}/ai/random-phrase`;
      if (queryParams.toString()) {
        url += `?${queryParams.toString()}`;
      }

      console.log(`Fetching AI-generated phrase from: ${url}`);

      const response = await fetch(url);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`API error (${response.status}): ${errorText}`);
        throw new Error(
          `Error fetching AI-generated phrase: ${response.status}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error("Error fetching AI-generated phrase:", error);
      throw error;
    } finally {
      hideLoading();
    }
  },

  /**
   * Get Google Gemini-generated random Haitian Kreyòl phrase
   * @param {Object} options - Optional parameters
   * @param {string} options.category - Optional category for the phrase
   * @param {number} options.difficultyLevel - Optional difficulty level (1-5)
   * @param {number} options.minWords - Optional minimum word count
   * @param {number} options.maxWords - Optional maximum word count
   * @returns {Promise<Object>} Object containing the generated phrase and metadata
   */
  async getGeminiPhrase(options = {}) {
    showLoading();
    try {
      // Build the query parameters
      const queryParams = new URLSearchParams();

      if (options.category) {
        queryParams.append("category", options.category);
      }

      if (options.difficultyLevel !== undefined) {
        queryParams.append("difficultyLevel", options.difficultyLevel);
      }

      if (options.minWords !== undefined) {
        queryParams.append("minWords", options.minWords);
      }

      if (options.maxWords !== undefined) {
        queryParams.append("maxWords", options.maxWords);
      }

      // Build the URL with query parameters
      let url = `${getApiUrl()}/ai/gemini-phrase`;
      if (queryParams.toString()) {
        url += `?${queryParams.toString()}`;
      }

      console.log(`Fetching Gemini-generated phrase from: ${url}`);

      const response = await fetch(url);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`API error (${response.status}): ${errorText}`);
        throw new Error(
          `Error fetching Gemini-generated phrase: ${response.status}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error("Error fetching Gemini-generated phrase:", error);
      throw error;
    } finally {
      hideLoading();
    }
  },
};

// Export the API Service using ES Module syntax
export default ApiService;
