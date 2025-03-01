# Talent Sync System

This project implements a synchronization system between a Job Seeker platform and a Talent Pool platform, with integration to a third-party matching service.

## System Components

1. **Job Seeker Service**: Provides APIs for receiving talent pool data and notifying about profile changes.
2. **Talent Pool Service**: Handles scheduled synchronization of talent pool data to the Job Seeker service.

## Prerequisites

- Docker and Docker Compose
- Git

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Leonard1004/talent-sync-system.git
cd talent-sync-system