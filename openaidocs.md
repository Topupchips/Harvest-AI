# OpenAI Platform Docs

> Developer documentation for the OpenAI Platform (https://platform.openai.com/docs).

Use this as a lightweight map for AI tools. Each doc page has a Markdown twin at `/docs/<slug>.md` for direct ingestion.

## Documentation sets
- [Platform docs (index)](https://platform.openai.com/docs/llms.txt)
- [Platform docs (full)](https://platform.openai.com/docs/llms-full.txt): Single-file Markdown export of the Platform docs.
- [Platform docs sitemap](https://platform.openai.com/docs/sitemap.xml)
- [OpenAPI spec](https://platform.openai.com/docs/static/api-definition.yaml)

## Get started
- [Developer quickstart](https://platform.openai.com/docs/quickstart.md): Learn how to use the OpenAI API to generate human-like responses to natural language prompts, analyze images with computer vision, use powerful built-in tools, and more.
- [Pricing](https://platform.openai.com/docs/pricing.md): Pricing information for the OpenAI platform.
- [Libraries](https://platform.openai.com/docs/libraries.md): Discover language-specific libraries for using the OpenAI API, including Python, Node.js, .NET, and more.
- [Docs MCP](https://platform.openai.com/docs/docs-mcp.md): Search and read OpenAI developer docs from your editor using MCP.
- [Using GPT-5.2](https://platform.openai.com/docs/guides/latest-model.md): Learn about how to use and migrate to GPT-5.2 and the GPT-5 model family, the latest models in the OpenAI API.

## Core concepts
- [Text generation](https://platform.openai.com/docs/guides/text.md): Learn how to use the OpenAI API to generate text from a prompt. Learn about message types and available text formats like JSON and Structured Outputs.
- [Code generation](https://platform.openai.com/docs/guides/code-generation.md): Learn how to use OpenAI Codex models to generate code and build coding agents.
- [Images and vision](https://platform.openai.com/docs/guides/images-vision.md): Learn how to understand or generate images with the OpenAI API.
- [Audio and speech](https://platform.openai.com/docs/guides/audio.md): Learn how to work with audio and speech in the OpenAI API.
- [Structured model outputs](https://platform.openai.com/docs/guides/structured-outputs.md): Understand how to ensure model responses follow specific JSON Schema you define.
- [Function calling](https://platform.openai.com/docs/guides/function-calling.md): Learn how function calling enables large language models to connect to external data and systems.
- [Migrate to the Responses API](https://platform.openai.com/docs/guides/migrate-to-responses.md)

## Agents
- [Agents](https://platform.openai.com/docs/guides/agents.md): Learn how to build agents and workflows with OpenAI and AgentKit.
- [Agent Builder](https://platform.openai.com/docs/guides/agent-builder.md): Use the OpenAI Agent Builder to start from templates, compose nodes, preview runs, and export workflows to code.
- [Node reference](https://platform.openai.com/docs/guides/node-reference.md): Explore all available nodes for composing workflows in Agent Builder.
- [Safety in building agents](https://platform.openai.com/docs/guides/agent-builder-safety.md): Minimize prompt injections and other risks when building agent workflows with OpenAI Agent Builder.
- [Agents SDK](https://platform.openai.com/docs/guides/agents-sdk.md): Learn how to build agents with the OpenAI Agents SDK.
- [ChatKit](https://platform.openai.com/docs/guides/chatkit.md): Embed a widget to build your own chat experiences.
- [Theming and customization in ChatKit](https://platform.openai.com/docs/guides/chatkit-themes.md): Configure colors, typography, density, and component variants in your ChatKit implementation.
- [ChatKit widgets](https://platform.openai.com/docs/guides/chatkit-widgets.md): Learn how to design widgets in your chat experience with ChatKit.
- [Actions in ChatKit](https://platform.openai.com/docs/guides/chatkit-actions.md): Embed a widget to build your own chat experiences.
- [Advanced integrations with ChatKit](https://platform.openai.com/docs/guides/custom-chatkit.md): Use your own server with ChatKit to integrate agent workflows into your product with more customization.
- [Agent evals](https://platform.openai.com/docs/guides/agent-evals.md): Use agent evals to create datasets, configure graders, and track evaluation runs for your agents.
- [Trace grading](https://platform.openai.com/docs/guides/trace-grading.md): Use trace grading to create datasets, configure graders, and track evaluation runs for your models.
- [Voice agents](https://platform.openai.com/docs/guides/voice-agents.md): Learn how to build agents that can work with audio and speech.

## Tools
- [Using tools](https://platform.openai.com/docs/guides/tools.md): Use powerful tools like remote MCP servers, or built-in tools like web search and file search to extend the model's capabilities.
- [Connectors and MCP servers](https://platform.openai.com/docs/guides/tools-connectors-mcp.md): Use remote MCP servers and OpenAI-maintained connectors for popular services to give models new capabilities.
- [Web search](https://platform.openai.com/docs/guides/tools-web-search.md): Allow models to search the web the latest information before generating a response.
- [Code Interpreter](https://platform.openai.com/docs/guides/tools-code-interpreter.md): Allow models to write and run Python to solve problems.
- [File search](https://platform.openai.com/docs/guides/tools-file-search.md): Allow models to search your files for relevant information before generating a response.
- [Retrieval](https://platform.openai.com/docs/guides/retrieval.md): Learn how to search your data using semantic similarity with the OpenAI API.
- [Image generation](https://platform.openai.com/docs/guides/tools-image-generation.md): Allow models to generate or edit images.
- [Computer use](https://platform.openai.com/docs/guides/tools-computer-use.md): Computer-using agent that can perform tasks on your behalf.
- [Local shell](https://platform.openai.com/docs/guides/tools-local-shell.md): Enable agents to run commands in a local shell.
- [Apply patch](https://platform.openai.com/docs/guides/tools-apply-patch.md): Allow models to propose structured diffs that your integration applies.
- [Shell](https://platform.openai.com/docs/guides/tools-shell.md): Allow models to run shell commands through your integration.

## Run and scale
- [Conversation state](https://platform.openai.com/docs/guides/conversation-state.md): Learn how to manage conversation state during a model interaction with the OpenAI API.
- [Background mode](https://platform.openai.com/docs/guides/background.md): Run long running tasks asynchronously in the background.
- [Streaming API responses](https://platform.openai.com/docs/guides/streaming-responses.md): Learn how to stream model responses from the OpenAI API using server-sent events.
- [Webhooks](https://platform.openai.com/docs/guides/webhooks.md)
- [File inputs](https://platform.openai.com/docs/guides/pdf-files.md): Learn how to use PDF files as inputs to the OpenAI API.
- [Prompting](https://platform.openai.com/docs/guides/prompting.md): Learn how to create, optimize, save, and reuse prompts with OpenAI models.
- [Prompt caching](https://platform.openai.com/docs/guides/prompt-caching.md): Learn how prompt caching reduces latency and cost for long prompts in OpenAI's API.
- [Prompt engineering](https://platform.openai.com/docs/guides/prompt-engineering.md): Learn strategies and tactics for better results using large language models in the OpenAI API.
- [Reasoning models](https://platform.openai.com/docs/guides/reasoning.md): Explore the capabilities of OpenAI's o1 series for complex reasoning and problem-solving. Learn about their features and how they compare to GPT-4o models.
- [Reasoning best practices](https://platform.openai.com/docs/guides/reasoning-best-practices.md): Explore best practices for using o-series reasoning models, like o1 and o3-mini, vs. GPT models—including use cases, how to choose a model, and prompting guidance.

## Evaluation
- [Getting started with datasets](https://platform.openai.com/docs/guides/evaluation-getting-started.md): Learn how to get started with evals using datasets.
- [Working with evals](https://platform.openai.com/docs/guides/evals.md): Learn how to test and improve AI model outputs through evaluations.
- [Prompt optimizer](https://platform.openai.com/docs/guides/prompt-optimizer.md): Learn how to use your dataset to automatically improve your prompts.
- [Evaluate external models](https://platform.openai.com/docs/guides/external-models.md): Learn how to run evals on non-OpenAI models, using the OpenAI platform.
- [Evaluation best practices](https://platform.openai.com/docs/guides/evaluation-best-practices.md): Learn best practices for designing evals to test and improve model performance in production.

## Realtime API
- [Realtime API](https://platform.openai.com/docs/guides/realtime.md): Learn how to build low-latency, multimodal LLM applications with the Realtime API.
- [Realtime API with WebRTC](https://platform.openai.com/docs/guides/realtime-webrtc.md): Learn how to connect to the Realtime API using WebRTC.
- [Realtime API with WebSocket](https://platform.openai.com/docs/guides/realtime-websocket.md): Learn how to connect to the Realtime API using WebSocket in a server-to-server application.
- [Realtime API with SIP](https://platform.openai.com/docs/guides/realtime-sip.md): Learn how to connect to the Realtime API using SIP.
- [Using realtime models](https://platform.openai.com/docs/guides/realtime-models-prompting.md): Learn how to use OpenAI realtime models and prompting effectively.
- [Realtime conversations](https://platform.openai.com/docs/guides/realtime-conversations.md): Learn how to manage Realtime speech-to-speech conversations.
- [Webhooks and server-side controls](https://platform.openai.com/docs/guides/realtime-server-controls.md): Learn how to use webhooks and server-side controls with the Realtime API.
- [Managing costs](https://platform.openai.com/docs/guides/realtime-costs.md): Learn how to monitor and optimize your costs when using the Realtime API.
- [Realtime transcription](https://platform.openai.com/docs/guides/realtime-transcription.md): Learn how to transcribe audio in real-time with the Realtime API.

## Model optimization
- [Model optimization](https://platform.openai.com/docs/guides/model-optimization.md)
- [Supervised fine-tuning](https://platform.openai.com/docs/guides/supervised-fine-tuning.md)
- [Vision fine-tuning](https://platform.openai.com/docs/guides/vision-fine-tuning.md)
- [Direct preference optimization](https://platform.openai.com/docs/guides/direct-preference-optimization.md)
- [Reinforcement fine-tuning](https://platform.openai.com/docs/guides/reinforcement-fine-tuning.md)
- [Reinforcement fine-tuning use cases](https://platform.openai.com/docs/guides/rft-use-cases.md): Explore best practices and practical use cases for reinforcement fine-tuning (RFT) with OpenAI models.
- [Fine-tuning best practices](https://platform.openai.com/docs/guides/fine-tuning-best-practices.md)
- [Graders](https://platform.openai.com/docs/guides/graders.md)

## Specialized models
- [Image generation](https://platform.openai.com/docs/guides/image-generation.md): Learn how to generate or edit images with the OpenAI API and image generation models.
- [Video generation with Sora](https://platform.openai.com/docs/guides/video-generation.md): Learn how to generate, refine, and manage videos using the OpenAI Sora Video API.
- [Text to speech](https://platform.openai.com/docs/guides/text-to-speech.md): Learn how to turn text into lifelike spoken audio with the OpenAI API.
- [Speech to text](https://platform.openai.com/docs/guides/speech-to-text.md): Learn how to turn audio into text with the OpenAI API.
- [Deep research](https://platform.openai.com/docs/guides/deep-research.md)
- [Vector embeddings](https://platform.openai.com/docs/guides/embeddings.md): Learn how to turn text into numbers, unlocking use cases like search, clustering, and more with OpenAI API embeddings.
- [Moderation](https://platform.openai.com/docs/guides/moderation.md): Learn how to use OpenAI's moderation endpoint to identify harmful content in text and images.

## Going live
- [Production best practices](https://platform.openai.com/docs/guides/production-best-practices.md): Explore best practices for transitioning your AI projects from prototype to production, including scaling, security, and cost management.
- [Latency optimization](https://platform.openai.com/docs/guides/latency-optimization.md): Improve latency across a wide variety of LLM-related use cases.
- [Predicted Outputs](https://platform.openai.com/docs/guides/predicted-outputs.md): Understand how to reduce latency for model responses where much of the response is known ahead of time.
- [Priority processing](https://platform.openai.com/docs/guides/priority-processing.md): Get faster processing in the API while retaining flexible pay-as-you-go pricing.
- [Cost optimization](https://platform.openai.com/docs/guides/cost-optimization.md): Lower your OpenAI model costs by trying our tools and strategies.
- [Batch API](https://platform.openai.com/docs/guides/batch.md): Learn how to use OpenAI's Batch API for processing jobs with asynchronous requests, increased rate limits, and cost efficiency.
- [Flex processing](https://platform.openai.com/docs/guides/flex-processing.md): Learn how to optimize costs for asynchronous tasks with flex processing.
- [Optimizing LLM Accuracy](https://platform.openai.com/docs/guides/optimizing-llm-accuracy.md): Learn strategies to enhance the accuracy of large language models using techniques like prompt engineering, retrieval-augmented generation, and fine-tuning.
- [Safety best practices](https://platform.openai.com/docs/guides/safety-best-practices.md): Learn how to implement safety measures like moderation, adversarial testing, human oversight, and prompt engineering to ensure responsible AI deployment.
- [Safety checks](https://platform.openai.com/docs/guides/safety-checks.md): Learn how OpenAI assesses for safety, OpenAI classifiers across safety categories, and implementation tips for how to pass safety checks.

## Specialized APIs
- [Assistants migration guide](https://platform.openai.com/docs/assistants/migration.md): Guidance for migrating from the Assistants API to the Responses API, including side-by-side comparisons and updated patterns.

## Resources
- [Data controls in the OpenAI platform](https://platform.openai.com/docs/guides/your-data.md): Your data is your data. An overview of how OpenAI uses your data, including retention and usage policies.
- [Manage permissions in the OpenAI platform](https://platform.openai.com/docs/guides/rbac.md): Learn how to use role-based access control to assign permissions, create custom roles, group users, and scope access across both the OpenAI API and dashboard.
- [Rate limits](https://platform.openai.com/docs/guides/rate-limits.md): Rate limits are restrictions that our API imposes on the number of times a user or client can access our services within a specified period of time.
- [Deprecations](https://platform.openai.com/docs/deprecations.md): Find information about OpenAI API deprecations and recommended replacements.
- [Building MCP servers for ChatGPT and API integrations](https://platform.openai.com/docs/mcp.md): Learn how to build MCP servers for use with ChatGPT connectors, deep research, or API integrations.
- [ChatGPT Developer mode](https://platform.openai.com/docs/guides/developer-mode.md)
- [GPT Actions](https://platform.openai.com/docs/actions/introduction.md): Learn about GPT Actions for customizing ChatGPT and interacting with external applications via APIs.
- [Getting started with GPT Actions](https://platform.openai.com/docs/actions/getting-started.md): Learn how to set up and test GPT actions from scratch with the OpenAI API.
- [GPT Actions library](https://platform.openai.com/docs/actions/actions-library.md): Learn how to build and integrate GPT Actions for common applications using OpenAI's guidance.
- [GPT Action authentication](https://platform.openai.com/docs/actions/authentication.md): Learn about authentication options for GPT actions, including no authentication, API key, and OAuth methods.
- [Production notes on GPT Actions](https://platform.openai.com/docs/actions/production.md): Guidelines for deploying GPT Actions in a production environment, including rate limits, timeouts, and security measures.
- [Data retrieval with GPT Actions](https://platform.openai.com/docs/actions/data-retrieval.md): Learn about performing data retrieval using APIs, relational databases, and vector databases with GPT Actions.
- [Sending and returning files with GPT Actions](https://platform.openai.com/docs/actions/sending-files.md): Learn how to send and return files using GPT Actions in the OpenAI API.

## Other
- [Overview of OpenAI Crawlers](https://platform.openai.com/docs/bots.md)
- [Key concepts](https://platform.openai.com/docs/concepts.md)
- [GPT Release Notes](https://platform.openai.com/docs/gpts/release-notes.md): Keep track of updates to OpenAI GPTs and explore new features and capabilities in the release notes.
- [Advanced usage](https://platform.openai.com/docs/guides/advanced-usage.md): Discover advanced usage techniques for OpenAI's API, including reproducible outputs, token management, and parameter settings.
- [Custom grammars](https://platform.openai.com/docs/guides/custom-grammars.md)
- [Custom tools](https://platform.openai.com/docs/guides/custom-tools.md)
- [Error codes](https://platform.openai.com/docs/guides/error-codes.md): An overview of error codes from the OpenAI API and Python library, including solutions and guidance.
- [Model selection](https://platform.openai.com/docs/guides/model-selection.md): Learn how to choose the right model by balancing accuracy, latency, and cost for optimal performance.
- [Prompt generation](https://platform.openai.com/docs/guides/prompt-generation.md): Learn how to generate prompts, functions, and schemas in the OpenAI API's Playground.
- [Voice activity detection (VAD)](https://platform.openai.com/docs/guides/realtime-vad.md): Learn about automatic voice activity detection in the Realtime API.
- [Supported countries and territories](https://platform.openai.com/docs/supported-countries.md)
- [Tutorials](https://platform.openai.com/docs/tutorials.md)
- [Meeting minutes](https://platform.openai.com/docs/tutorials/meeting-minutes.md)
- [Web QA with embeddings](https://platform.openai.com/docs/tutorials/web-qa-embeddings.md)