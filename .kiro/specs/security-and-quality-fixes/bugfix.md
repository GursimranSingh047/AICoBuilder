# Bugfix Requirements Document

## Introduction

This document addresses critical security vulnerabilities, dependency issues, and code quality problems discovered during comprehensive testing of the ProjectPilot (AI Co-Builder) application. The application is a full-stack system with a FastAPI backend and React frontend that generates AI-powered project code.

The bugs identified pose significant security risks including:
- **Exposed API credentials** in source code and version control
- **Unpatched security vulnerabilities** in frontend dependencies
- **Missing security controls** (rate limiting, input validation, security headers)
- **Configuration management issues** preventing environment-based deployments
- **Code quality problems** affecting maintainability

These issues must be systematically fixed while preserving all existing functional behavior of the application.

---

## Bug Analysis

### 1. Current Behavior (Defect)

#### 1.1 Hardcoded Secrets in Source Code

**1.1.1** WHEN the backend application starts THEN the system prints a hardcoded Google/Gemini API key to console output via `print("KEY:", os.getenv("AIzaSyDYkFadYYfPKPiZl6hnwaczk1B0f5jI5FM"))` in backend/main.py line 10

**1.1.2** WHEN the backend/.env file is examined THEN the system exposes an OpenAI API key `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` in plain text

**1.1.3** WHEN the repository is cloned or version control history is examined THEN the system may expose the .env file containing secrets if not properly excluded by .gitignore

**1.1.4** WHEN application logs are generated THEN the system may leak sensitive information through the hardcoded API key print statement

#### 1.2 Vulnerable Dependencies

**1.2.1** WHEN `npm audit` is run in the frontend directory THEN the system reports 7 moderate severity vulnerabilities in dependencies (axios 1.0.0-1.14.0, esbuild <=0.24.2, follow-redirects <=1.15.11, prismjs <1.30.0)

**1.2.2** WHEN the frontend application uses axios versions 1.0.0-1.14.0 THEN the system is vulnerable to SSRF and metadata exfiltration attacks

**1.2.3** WHEN the frontend development server uses esbuild <=0.24.2 THEN the system is vulnerable to development server request vulnerabilities

**1.2.4** WHEN the frontend uses follow-redirects <=1.15.11 THEN the system is vulnerable to authentication header leakage

**1.2.5** WHEN the frontend uses prismjs <1.30.0 THEN the system is vulnerable to DOM clobbering attacks

#### 1.3 Missing Security Controls

**1.3.1** WHEN a user makes unlimited rapid requests to /auth/signup THEN the system accepts all requests without rate limiting, enabling brute force attacks

**1.3.2** WHEN a user makes unlimited rapid requests to /auth/login THEN the system accepts all requests without rate limiting, enabling credential stuffing attacks

**1.3.3** WHEN a user makes unlimited rapid requests to /projects/generate THEN the system accepts all requests without rate limiting, enabling resource exhaustion and DoS attacks

**1.3.4** WHEN a user makes unlimited rapid requests to /chat/ THEN the system accepts all requests without rate limiting, enabling API abuse

**1.3.5** WHEN HTTP responses are sent to the browser THEN the system does not include security headers (Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Strict-Transport-Security, Referrer-Policy)

#### 1.4 Input Validation Vulnerabilities

**1.4.1** WHEN user-provided `project_name` contains path traversal sequences (e.g., "../../../etc/passwd") in /projects/generate THEN the system uses the unsanitized input in file operations without validation

**1.4.2** WHEN user-provided `idea` contains special characters or command injection payloads in /projects/generate THEN the system processes the unsanitized input without proper escaping

**1.4.3** WHEN user input is used to construct file paths in project_generator service THEN the system does not validate or sanitize the input, enabling potential file system manipulation

#### 1.5 Configuration Management Issues

**1.5.1** WHEN the frontend API client is initialized THEN the system uses a hardcoded baseURL `'http://127.0.0.1:8000'` in frontend/src/api/client.js

**1.5.2** WHEN the application needs to be deployed to staging or production environments THEN the system cannot easily switch API endpoints without modifying source code

**1.5.3** WHEN the frontend download URL is constructed THEN the system uses a hardcoded URL `'http://127.0.0.1:8000/projects/${id}/download'` in projectsAPI.downloadUrl

#### 1.6 Code Quality Issues

**1.6.1** WHEN backend/main.py is parsed THEN the system contains duplicate imports: `from contextlib import asynccontextmanager` appears on lines 7 and 11, and `from fastapi import FastAPI, Request` appears on lines 8 and 12

**1.6.2** WHEN the codebase is analyzed for maintainability THEN the system has redundant import statements that reduce code quality

#### 1.7 Error Handling Information Disclosure

**1.7.1** WHEN an unhandled exception occurs in the backend THEN the system logs the full exception details which may expose internal implementation details, stack traces, or sensitive data paths

**1.7.2** WHEN error responses are returned to clients THEN the system may inadvertently leak information about the internal architecture through generic error messages combined with detailed logs

#### 1.8 Dependency Installation Issues

**1.8.1** WHEN a new developer clones the repository and attempts to run the backend THEN the system fails because dependencies (loguru, etc.) are not installed

**1.8.2** WHEN a new developer clones the repository and attempts to run the frontend THEN the system fails because node_modules are not installed

**1.8.3** WHEN the application is deployed to a new environment THEN the system requires manual intervention to install dependencies

#### 1.9 Missing .gitignore Configuration

**1.9.1** WHEN the repository is initialized THEN the system does not have a .gitignore file at the root level

**1.9.2** WHEN sensitive files like .env are created THEN the system may accidentally commit them to version control without proper exclusion rules

**1.9.3** WHEN virtual environments, node_modules, or build artifacts are created THEN the system may accidentally commit large binary files to version control

---

### 2. Expected Behavior (Correct)

#### 2.1 Secure Secret Management

**2.1.1** WHEN the backend application starts THEN the system SHALL NOT print, log, or expose any API keys or secrets to console output or logs

**2.1.2** WHEN API keys are needed THEN the system SHALL load them exclusively from environment variables using os.getenv() without hardcoded fallback values

**2.1.3** WHEN the repository is cloned THEN the system SHALL include a .gitignore file that excludes .env files from version control

**2.1.4** WHEN developers need to configure the application THEN the system SHALL provide a .env.example file with placeholder values (not real secrets)

**2.1.5** WHEN the backend/.env file exists THEN the system SHALL ensure it is listed in .gitignore and never committed to version control

#### 2.2 Patched Dependencies

**2.2.1** WHEN `npm audit` is run in the frontend directory THEN the system SHALL report zero high or critical severity vulnerabilities

**2.2.2** WHEN the frontend package.json is examined THEN the system SHALL specify axios version ^1.7.2 or higher (patched version)

**2.2.3** WHEN the frontend uses esbuild THEN the system SHALL use version >0.24.2 (patched version)

**2.2.4** WHEN the frontend uses follow-redirects THEN the system SHALL use version >1.15.11 (patched version)

**2.2.5** WHEN the frontend uses prismjs THEN the system SHALL use version >=1.30.0 (patched version)

**2.2.6** WHEN dependencies are updated THEN the system SHALL run `npm audit fix` to automatically patch vulnerabilities where possible

#### 2.3 Implemented Security Controls

**2.3.1** WHEN a user makes more than 5 requests per minute to /auth/signup THEN the system SHALL return HTTP 429 (Too Many Requests) and block further requests for 1 minute

**2.3.2** WHEN a user makes more than 10 requests per minute to /auth/login THEN the system SHALL return HTTP 429 (Too Many Requests) and block further requests for 1 minute

**2.3.3** WHEN a user makes more than 3 requests per minute to /projects/generate THEN the system SHALL return HTTP 429 (Too Many Requests) and block further requests for 5 minutes

**2.3.4** WHEN a user makes more than 20 requests per minute to /chat/ THEN the system SHALL return HTTP 429 (Too Many Requests) and block further requests for 1 minute

**2.3.5** WHEN HTTP responses are sent to the browser THEN the system SHALL include security headers:
- Content-Security-Policy: default-src 'self'
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Strict-Transport-Security: max-age=31536000; includeSubDomains (production only)
- Referrer-Policy: strict-origin-when-cross-origin

#### 2.4 Input Validation and Sanitization

**2.4.1** WHEN user-provided `project_name` is received in /projects/generate THEN the system SHALL validate it against a whitelist pattern (alphanumeric, hyphens, underscores only) and reject invalid input with HTTP 400

**2.4.2** WHEN user-provided `project_name` contains path traversal sequences THEN the system SHALL reject the request with HTTP 400 and error message "Invalid project name"

**2.4.3** WHEN user-provided `idea` is received THEN the system SHALL sanitize it by removing or escaping special characters that could be used for injection attacks

**2.4.4** WHEN constructing file paths from user input THEN the system SHALL use Path().resolve() to normalize paths and validate they remain within the intended directory

**2.4.5** WHEN user input exceeds reasonable length limits THEN the system SHALL reject requests with HTTP 400 (e.g., project_name max 100 chars, idea max 5000 chars)

#### 2.5 Environment-Based Configuration

**2.5.1** WHEN the frontend API client is initialized THEN the system SHALL read the baseURL from an environment variable (VITE_API_BASE_URL) with a development default

**2.5.2** WHEN the application is built for production THEN the system SHALL use the production API URL from environment variables

**2.5.3** WHEN the frontend download URL is constructed THEN the system SHALL use the configured baseURL instead of a hardcoded value

**2.5.4** WHEN environment variables are not set THEN the system SHALL fall back to sensible development defaults (http://127.0.0.1:8000 for local development)

#### 2.6 Clean Code Quality

**2.6.1** WHEN backend/main.py is parsed THEN the system SHALL contain no duplicate import statements

**2.6.2** WHEN the codebase is analyzed THEN the system SHALL have each import statement appear exactly once at the top of each file

**2.6.3** WHEN the hardcoded API key print statement is removed THEN the system SHALL remove the entire line including the malformed os.getenv() call

#### 2.7 Secure Error Handling

**2.7.1** WHEN an unhandled exception occurs THEN the system SHALL log minimal information (error type and timestamp) without exposing stack traces, file paths, or sensitive data in logs

**2.7.2** WHEN error responses are returned to clients THEN the system SHALL return generic error messages (e.g., "An unexpected error occurred") without exposing internal implementation details

**2.7.3** WHEN errors are logged for debugging THEN the system SHALL use appropriate log levels (ERROR for exceptions) and ensure logs are not exposed to end users

#### 2.8 Documented Dependency Installation

**2.8.1** WHEN a new developer clones the repository THEN the system SHALL provide clear README instructions for installing backend dependencies (`pip install -r requirements.txt`)

**2.8.2** WHEN a new developer clones the repository THEN the system SHALL provide clear README instructions for installing frontend dependencies (`npm install`)

**2.8.3** WHEN the backend requirements.txt is examined THEN the system SHALL include all necessary dependencies with pinned versions

**2.8.4** WHEN the frontend package.json is examined THEN the system SHALL include all necessary dependencies with version ranges

#### 2.9 Proper .gitignore Configuration

**2.9.1** WHEN the repository is initialized THEN the system SHALL include a comprehensive .gitignore file at the root level

**2.9.2** WHEN the .gitignore file is examined THEN the system SHALL exclude:
- .env and .env.* files (except .env.example)
- Python virtual environments (.venv/, venv/, env/)
- Python cache (__pycache__/, *.pyc, *.pyo)
- Node.js dependencies (node_modules/)
- Build artifacts (dist/, build/, *.zip)
- IDE files (.vscode/, .idea/, *.swp)
- Database files (*.db, *.sqlite)
- Log files (*.log, logs/)

**2.9.3** WHEN sensitive files are created THEN the system SHALL automatically exclude them from version control via .gitignore rules

---

### 3. Unchanged Behavior (Regression Prevention)

#### 3.1 Authentication Functionality

**3.1.1** WHEN a user signs up with valid credentials (email, username, password) THEN the system SHALL CONTINUE TO create a new user account and return an access token

**3.1.2** WHEN a user logs in with valid credentials THEN the system SHALL CONTINUE TO authenticate the user and return an access token

**3.1.3** WHEN a user accesses /auth/me with a valid token THEN the system SHALL CONTINUE TO return the user's profile information

**3.1.4** WHEN a user provides invalid credentials THEN the system SHALL CONTINUE TO return HTTP 401 with "Invalid email or password"

#### 3.2 Project Generation Functionality

**3.2.1** WHEN a user submits a valid project idea to /projects/generate THEN the system SHALL CONTINUE TO generate a complete project with code files, folder structure, and README

**3.2.2** WHEN a project is generated successfully THEN the system SHALL CONTINUE TO create a database record with status "completed"

**3.2.3** WHEN a project generation fails THEN the system SHALL CONTINUE TO update the database record with status "failed"

**3.2.4** WHEN a user requests /projects/{id}/download THEN the system SHALL CONTINUE TO return the project as a ZIP file

**3.2.5** WHEN a user lists projects via /projects/ THEN the system SHALL CONTINUE TO return paginated project summaries

#### 3.3 Chat Functionality

**3.3.1** WHEN a user sends a chat message to /chat/ THEN the system SHALL CONTINUE TO generate an AI response using the Gemini service

**3.3.2** WHEN a user provides a project_id in the chat request THEN the system SHALL CONTINUE TO include project context in the AI response

**3.3.3** WHEN a user requests code improvement via /chat/improve THEN the system SHALL CONTINUE TO return improved code based on the instruction

**3.3.4** WHEN a user requests code explanation via /chat/explain THEN the system SHALL CONTINUE TO return a plain-English explanation

#### 3.4 ML Suggestions Functionality

**3.4.1** WHEN a user requests project suggestions via /suggest/ THEN the system SHALL CONTINUE TO predict project type, tech stack, and features using the ML model

**3.4.2** WHEN a user requests available stacks via /suggest/stacks THEN the system SHALL CONTINUE TO return the STACK_MAP

**3.4.3** WHEN a user requests features for a project type via /suggest/features/{type} THEN the system SHALL CONTINUE TO return suggested features from FEATURES_MAP

#### 3.5 CORS and Middleware

**3.5.1** WHEN the frontend makes cross-origin requests to the backend THEN the system SHALL CONTINUE TO allow requests from configured origins

**3.5.2** WHEN CORS is configured THEN the system SHALL CONTINUE TO allow credentials, all methods, and all headers as currently configured

#### 3.6 Database Operations

**3.6.1** WHEN the application starts THEN the system SHALL CONTINUE TO initialize the database using init_db()

**3.6.2** WHEN database queries are executed THEN the system SHALL CONTINUE TO use SQLAlchemy ORM with the existing models

**3.6.3** WHEN projects are created, updated, or deleted THEN the system SHALL CONTINUE TO persist changes to the database

#### 3.7 Logging Behavior

**3.7.1** WHEN the application starts THEN the system SHALL CONTINUE TO set up logging using loguru with the existing configuration

**3.7.2** WHEN significant events occur (user registration, login, project generation) THEN the system SHALL CONTINUE TO log informational messages

**3.7.3** WHEN errors occur THEN the system SHALL CONTINUE TO log error messages (but with improved security as per section 2.7)

#### 3.8 API Documentation

**3.8.1** WHEN a user accesses /docs THEN the system SHALL CONTINUE TO display the interactive Swagger UI documentation

**3.8.2** WHEN a user accesses /redoc THEN the system SHALL CONTINUE TO display the ReDoc documentation

**3.8.3** WHEN a user accesses / or /health THEN the system SHALL CONTINUE TO return health check responses

#### 3.9 Frontend User Interface

**3.9.1** WHEN the frontend application loads THEN the system SHALL CONTINUE TO display the login, signup, dashboard, generator, chat, and project viewer pages

**3.9.2** WHEN a user interacts with the UI THEN the system SHALL CONTINUE TO make API requests using the axios client

**3.9.3** WHEN API responses are received THEN the system SHALL CONTINUE TO handle success and error cases appropriately

#### 3.10 File Generation and Storage

**3.10.1** WHEN projects are generated THEN the system SHALL CONTINUE TO create files in the backend/generated_projects/ directory

**3.10.2** WHEN projects are zipped THEN the system SHALL CONTINUE TO create .zip files in the backend/generated_projects/ directory

**3.10.3** WHEN project files are stored in the database THEN the system SHALL CONTINUE TO store previews (first 500 chars) in the generated_files column

---

## Bug Condition Derivation

### Bug Condition Function

```pascal
FUNCTION isBugCondition(X)
  INPUT: X of type ApplicationState
  OUTPUT: boolean
  
  // Returns true when any security vulnerability or quality issue exists
  RETURN (
    hasHardcodedSecrets(X) OR
    hasVulnerableDependencies(X) OR
    lacksRateLimiting(X) OR
    lacksInputValidation(X) OR
    hasHardcodedConfig(X) OR
    hasDuplicateImports(X) OR
    lacksSecurityHeaders(X) OR
    hasInsecureErrorHandling(X) OR
    lacksDependencyDocs(X) OR
    lacksGitignore(X)
  )
END FUNCTION

WHERE:
  hasHardcodedSecrets(X) := 
    X.backend.main_py contains hardcoded API key print statement OR
    X.backend.env_file is not in gitignore
    
  hasVulnerableDependencies(X) :=
    X.frontend.npm_audit_vulnerabilities > 0
    
  lacksRateLimiting(X) :=
    X.backend.endpoints["/auth/signup"].rate_limit = null OR
    X.backend.endpoints["/auth/login"].rate_limit = null OR
    X.backend.endpoints["/projects/generate"].rate_limit = null OR
    X.backend.endpoints["/chat/"].rate_limit = null
    
  lacksInputValidation(X) :=
    X.backend.endpoints["/projects/generate"].validates_project_name = false OR
    X.backend.endpoints["/projects/generate"].sanitizes_idea = false
    
  hasHardcodedConfig(X) :=
    X.frontend.api_client.baseURL is hardcoded
    
  hasDuplicateImports(X) :=
    X.backend.main_py has duplicate import statements
    
  lacksSecurityHeaders(X) :=
    X.backend.response_headers lacks CSP, X-Frame-Options, etc.
    
  hasInsecureErrorHandling(X) :=
    X.backend.exception_handler exposes internal details
    
  lacksDependencyDocs(X) :=
    X.readme lacks installation instructions
    
  lacksGitignore(X) :=
    X.root_directory lacks .gitignore file
```

### Property Specification: Fix Checking

```pascal
// Property: Security Vulnerabilities Fixed
FOR ALL X WHERE isBugCondition(X) DO
  result ← applySecurityFixes(X)
  
  ASSERT NOT hasHardcodedSecrets(result)
  ASSERT NOT hasVulnerableDependencies(result)
  ASSERT hasRateLimiting(result, "/auth/signup", 5, 60)
  ASSERT hasRateLimiting(result, "/auth/login", 10, 60)
  ASSERT hasRateLimiting(result, "/projects/generate", 3, 300)
  ASSERT hasRateLimiting(result, "/chat/", 20, 60)
  ASSERT hasInputValidation(result, "project_name")
  ASSERT hasInputValidation(result, "idea")
  ASSERT hasEnvironmentConfig(result, "VITE_API_BASE_URL")
  ASSERT NOT hasDuplicateImports(result)
  ASSERT hasSecurityHeaders(result)
  ASSERT hasSecureErrorHandling(result)
  ASSERT hasDependencyDocs(result)
  ASSERT hasGitignore(result)
END FOR
```

### Property Specification: Preservation Checking

```pascal
// Property: Existing Functionality Preserved
FOR ALL X WHERE NOT isBugCondition(X) DO
  ASSERT applySecurityFixes(X) = X
END FOR

// Property: Functional Behavior Unchanged
FOR ALL request IN validRequests DO
  original_response ← handleRequest(unfixed_app, request)
  fixed_response ← handleRequest(fixed_app, request)
  
  // Responses should be identical except for:
  // 1. Rate-limited requests (new 429 responses)
  // 2. Invalid input (new 400 responses for malicious input)
  // 3. Security headers (added to all responses)
  
  IF NOT isRateLimited(request) AND NOT isMaliciousInput(request) THEN
    ASSERT original_response.body = fixed_response.body
    ASSERT original_response.status_code = fixed_response.status_code
  END IF
END FOR
```

### Counterexamples

**Counterexample 1: Hardcoded API Key**
```python
# Current (buggy) code in backend/main.py line 10:
print("KEY:", os.getenv("AIzaSyDYkFadYYfPKPiZl6hnwaczk1B0f5jI5FM"))
# This exposes the API key in console output and logs
```

**Counterexample 2: Missing Rate Limiting**
```python
# Current (buggy) code - no rate limiting on /auth/login:
@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    # Accepts unlimited requests - vulnerable to brute force
```

**Counterexample 3: Unvalidated Input**
```python
# Current (buggy) code in /projects/generate:
project_name = payload.project_name  # No validation
# User could provide: "../../../etc/passwd"
```

**Counterexample 4: Vulnerable Dependencies**
```json
// Current (buggy) frontend/package.json:
"axios": "^1.7.2"  // Has known SSRF vulnerabilities in 1.0.0-1.14.0
```

**Counterexample 5: Hardcoded Configuration**
```javascript
// Current (buggy) frontend/src/api/client.js:
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',  // Cannot change for production
})
```

---

## Summary

This bugfix addresses **10 categories of security and quality issues** affecting the ProjectPilot application:

1. **Hardcoded secrets** - API keys in source code and logs
2. **Vulnerable dependencies** - 7 npm security vulnerabilities
3. **Missing rate limiting** - No protection against abuse on 4 critical endpoints
4. **Input validation gaps** - Path traversal and injection vulnerabilities
5. **Configuration management** - Hardcoded URLs preventing environment-based deployment
6. **Code quality** - Duplicate imports reducing maintainability
7. **Security headers** - Missing browser security protections
8. **Error handling** - Information disclosure through logs
9. **Dependency documentation** - Missing installation instructions
10. **Version control** - Missing .gitignore allowing secrets in repository

The fixes will eliminate all security vulnerabilities while preserving 100% of existing functional behavior across authentication, project generation, chat, ML suggestions, and all other features.
