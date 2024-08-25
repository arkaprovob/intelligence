# DocsBot: Your One-Stop Documentation Solution

## What is DocsBot?

DocsBot is an early-stage GenAI application designed to improve how developers access and search technical
documentation. The project's core purpose? To save developers time and streamline their workflow by consolidating all
documentation needs into one intelligent, easy-to-use platform.

## The Idea Behind DocsBot

Ever felt frustrated searching multiple spaces for that one piece of API information or architecture diagram? We've been
there too! That's why we created DocsBot. Here's what makes it special:

- **Unified Search**: No more juggling between different documentation sources. DocsBot brings everything together in
  one place.
- **Intelligent Retrieval**: Powered by GenAI, DocsBot doesn't just store docs – it understands them. Ask a question,
  and it'll either provide the answer or point you to the exact location in the source.
- **Time-Saving**: According to a [Stack Overflow survey 2023](https://survey.stackoverflow.co/2023/), 10 developers
  spend an average of 108 hours per year searching for answers or solutions to work-related problems. That's valuable
  time we're aiming to give back to you!

## Why DocsBot?

In today's fast-paced development environment, quick access to accurate information is crucial. DocsBot addresses this
need by:

1. Consolidating information from multiple sources
2. Providing context-aware search capabilities
3. Pinpointing exact locations in documents for detailed information
4. Understanding complex relationships between different pieces of documentation
5. Reducing the time spent searching for answers, allowing developers to focus on what they do best – coding!

By leveraging the power of GenAI, DocsBot can find connections that might not be immediately obvious, ensuring you get
the most relevant and useful information every time.

## Current State and Future Plans

DocsBot is currently in its early stages, focusing on core functionalities due to resource constraints. Here's what we'
re working with:

- **GGUF model**: For finding connections between documents
- **Qdrant vector database**: To store documents and excerpts
- **PostgreSQL**: For saving feedback and application states
- **LlamaIndex framework**: The backbone of our solution

As we move forward, we plan to add more advanced features while maintaining a balance between accuracy, speed, and
convenience.

## Getting Started

### Prerequisites

To set up DocsBot (tested on Mac Silicon, should work on Linux and Windows), you'll need:

- Podman
- Qdrant
- PostgreSQL
- Redis

### Setup Instructions

1. **Create a network:**
   ```
   podman network create docsbot
   ```

2. **Create storage directories:**
   ```
   mkdir qdrant_storage
   mkdir db
   ```

3. **Set up dependency containers:**
   ```
   podman run --network docsbot -d --name docsbotqdrant -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage:z qdrant/qdrant
   podman run --network docsbot -d --name docsbotredis -p 6379:6379 redis/redis-stack-server
   podman run --network docsbot -d \
     --name docsbotpostgres \
     -p 5432:5432 \
     -e POSTGRES_PASSWORD=R@nD0M202$ \
     -e PGDATA=/var/lib/postgresql/data/pgdata \
     -v $(pwd)/db:/var/lib/postgresql/data:z \
     postgres
   ```

4. **Download the model:**
   ```
   curl -LO https://huggingface.co/bartowski/Phi-3.1-mini-4k-instruct-GGUF/resolve/main/Phi-3.1-mini-4k-instruct-Q8_0.gguf
   ```

5. **Build the backend service:**
   Navigate to the project's root directory and run:
   ```
   podman build -t docsbot-app .
   ```

6. **Run the service:**
   ```
   podman run --network docsbot -p 8000:8000 \
     -v <model_dir>:/app/model:Z \
     -e PROFILE=production \
     -e MODEL_PATH=/app/model/Phi-3.1-mini-4k-instruct-Q8_0.gguf \
     -e DB_HOST=docsbotpostgres \
     -e QDRANT_HOST=docsbotqdrant \
     docsbot-app
   ```
   Replace `<model_dir>` with the directory where your Phi model is stored.


7. **Access the DocsBot interface:**
   Once the service is up and running, open your web browser and navigate to:
   [http://localhost:8000/static/home.html](http://localhost:8000/static/home.html)

## Optional: Testing Network Accessibility

To ensure all services are accessible within the DocsBot network, run:

```
podman run -it --rm --name network-test --network=docsbot alpine sh
```

Then test the services using commands like:

```
wget docsbotqdrant:6333
```

or

```
curl docsbotqdrant:6333
```

These should return an HTTP status.

## Contribute

We're always looking for ways to improve DocsBot! If you have ideas, bug reports, or want to contribute code, please
feel free to open an issue or submit a pull request.

## Stay Connected

Join us on this exciting journey to revolutionize documentation searching! Follow our progress and share your thoughts –
we'd love to hear from you.

Happy coding, and may you never lose another minute searching for that elusive piece of documentation again!