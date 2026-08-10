# Prompt Detective Frontend

A modern React + TypeScript application for AI-powered video and image analysis.

## Features

- **Modern Stack**: React 18, TypeScript, Vite, TailwindCSS
- **Authentication**: JWT-based auth with refresh tokens
- **File Upload**: Drag-and-drop interface with progress tracking
- **Real-time Updates**: WebSocket integration for job status
- **Responsive Design**: Mobile-first responsive UI
- **State Management**: Zustand for client-side state
- **API Client**: Axios with interceptors and error handling

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout.tsx      # Main layout with navigation
│   ├── UploadComponent.tsx  # File upload with progress
│   ├── ProtectedRoute.tsx   # Route authentication
│   └── LoadingSpinner.tsx   # Loading states
├── pages/              # Route components
│   ├── LandingPage.tsx # Marketing homepage
│   ├── LoginPage.tsx   # User authentication
│   ├── SignupPage.tsx  # User registration
│   ├── DashboardPage.tsx    # Main app interface
│   ├── PricingPage.tsx # Subscription plans
│   ├── ProfilePage.tsx # User settings
│   └── AdminPage.tsx   # Admin interface
├── hooks/              # Custom React hooks
│   ├── useAuth.ts      # Authentication logic
│   └── useUpload.ts    # File upload logic
├── services/           # API and external services
│   └── api.ts          # Axios HTTP client
├── stores/             # State management
│   └── authStore.ts    # User authentication state
├── types/              # TypeScript type definitions
└── utils/              # Helper functions
```

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   ```
   
   Update `.env` with your backend API URL:
   ```env
   VITE_API_URL=http://localhost:8000/api/v1
   VITE_APP_TITLE=Prompt Detective
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:3000`

### Backend Integration

The frontend expects the backend API to be running at `http://localhost:8000` by default. Key endpoints:

- `POST /api/v1/auth/signup` - User registration
- `POST /api/v1/auth/login` - User authentication  
- `POST /api/v1/uploads` - File upload
- `GET /api/v1/jobs/{id}` - Job status tracking
- `GET /api/v1/jobs/{id}/results` - Analysis results

### Build for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` directory.

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler

### Code Quality

The project includes:

- **ESLint** for code linting
- **TypeScript** for type safety
- **Prettier** for code formatting (optional)
- **Husky** for git hooks (optional)

### Testing

```bash
npm run test        # Run tests
npm run test:watch  # Run tests in watch mode
```

## Architecture

### Authentication Flow

1. User logs in via `/login`
2. Backend returns JWT access + refresh tokens
3. Tokens stored in Zustand store (persisted to localStorage)
4. API requests include `Authorization: Bearer <token>` header
5. Expired tokens automatically refreshed via interceptor

### File Upload Process

1. User drags/drops file on upload component
2. File validated (type, size limits)
3. Upload to `/uploads` endpoint with progress tracking
4. Backend returns job ID
5. Frontend polls job status until completion
6. Results displayed when analysis complete

### State Management

- **Authentication**: Zustand store with localStorage persistence
- **API State**: React Query for server state caching
- **Form State**: React Hook Form for form management
- **UI State**: Local component state with useState

## Deployment

### Environment Variables

Production deployment requires:

```env
VITE_API_URL=https://your-api-domain.com/api/v1
VITE_APP_TITLE=Prompt Detective
```

### Static Hosting

The built application can be deployed to:

- **Vercel** (recommended)
- **Netlify**
- **AWS S3 + CloudFront**
- **Any static hosting service**

### Docker Deployment

```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.