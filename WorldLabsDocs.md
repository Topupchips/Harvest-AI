# Tools & examples
Source: https://docs.worldlabs.ai/api/examples

End-to-end examples for learning how to use the World API. These projects are intended for experimentation, not production use.

## API examples (Node & Python)

Minimal scripts and a simple web app for generating worlds using the raw API.

<Icon icon="arrow-up-right" /> [View on GitHub](https://github.com/worldlabsai/worldlabs-api-examples)

## Client & splat utilities (Python)

Python client and utilities for saving/loading splats and rendering out videos.

<Icon icon="arrow-up-right" /> [View on GitHub](https://github.com/worldlabsai/worldlabs-api-python)

## Spark

Render worlds on the web with SparkJS.

SparkJS is a high-performance 3D Gaussian splatting renderer built on top of THREE.js.
It is the recommended way to render World Labs splat assets in the browser.

Spark supports:

* Fast splat rendering on desktop and mobile
* Integration with other THREE.js meshes
* SPZ, PLY, SOGS, KSPLAT, and SPLAT formats
* Dynamic and procedural splat effects

<Icon icon="arrow-up-right" /> [Explore SparkJS](https://sparkjs.dev/)


# Frequently asked questions
Source: https://docs.worldlabs.ai/api/faq

Common questions and answers about the World API

### Can I retrieve PLY files from the API?

The World Labs API currently returns scene geometry in **.spz (3D Gaussian Splat)** format only. Direct export of .ply files via the API is not supported.

For production or large-scale workflows, .spz files should be converted programmatically using existing libraries:

* C++: [https://github.com/nianticlabs/spzJavaScript](https://github.com/nianticlabs/spzJavaScript)
* TypeScript: [https://github.com/arrival-space/spz-js](https://github.com/arrival-space/spz-js)

For small-scale or one-off use, a hosted web tool is available for ad-hoc conversion: [https://spz-to-ply.netlify.app](https://spz-to-ply.netlify.app)

### How does API billing work?

Billing for the World API is separate from billing for the Marble web app.

* Credits purchased for the Marble app cannot be used with the API
* API usage requires credits purchased through the World Labs Platform

If you plan to use the API, make sure you purchase credits on the World Labs Platform, NOT in the Marble app.

### What is the difference between the `Marble 0.1-mini` and `Marble 0.1-plus` models? When should I use each?

World Labs offers two model variants for scene generation:

* `Marble 0.1-mini` is optimized for **speed and cost**. It’s best suited for rapid iteration, previews, testing, and large-scale batch jobs where throughput matters more than maximum fidelity.
* `Marble 0.1-plus` prioritizes **higher visual quality and detail**. It’s recommended for final assets, production scenes, and use cases where accuracy and realism are important.

**Best practice**: Use `Marble 0.1-mini` during development and experimentation, then switch to `Marble 0.1-plus` for final or customer-facing outputs.

### Where can I read more about World Labs policies?

Please view our [Terms of Service](/terms-of-service) and [Privacy Policy](/privacy-policy) for details.


# Quickstart
Source: https://docs.worldlabs.ai/api/index

Learn how to use the World API

## Quickstart

<Steps>
  <Step title="Get an API key">
    <Steps>
      <Step>
        Sign in to the [World Labs Platform](https://platform.worldlabs.ai) with your Marble account.

        If you don't have a Marble account, you'll be prompted to create one.
      </Step>

      <Step>
        Visit the [billing page](https://platform.worldlabs.ai/billing).

        Add a payment method to your account and then purchase some credits to get started.
      </Step>

      <Step>
        Generate an API key from the [API keys page](https://platform.worldlabs.ai/api-keys).

        <Warning>
          Save your API key in a secure location and never share it with anyone.
        </Warning>
      </Step>
    </Steps>
  </Step>

  <Step title="Create your first world">
    To verify your development setup is working, we recommend creating a world from only a text prompt.

    You can also create a world from an image, multiple images of the same scene, or a video.

    <Note>
      Iterate more quickly with `Marble 0.1-mini` (equivalent to Draft in Marble).

      This example uses `Marble 0.1-plus` by default for best quality. If you’re iterating or debugging, you can use `Marble 0.1-mini` for much faster (30-45s) and cheaper generations.

      To use it, add `"model": "Marble 0.1-mini"` to your request body.
    </Note>

    <Tabs>
      <Tab title="Text input">
        <Steps>
          <Step>
            Make a `POST` request to the [`/marble/v1/worlds:generate`](/api/reference/worlds/generate) endpoint.

            <CodeGroup>
              ```bash Request theme={null}
              curl -X POST 'https://api.worldlabs.ai/marble/v1/worlds:generate' \
                -H 'Content-Type: application/json' \
                -H 'WLT-Api-Key: YOUR_API_KEY' \
                -d '{
                  "display_name": "Mystical Forest",
                  "world_prompt": {
                    "type": "text",
                    "text_prompt": "A mystical forest with glowing mushrooms"
                  }
                }'
              ```

              ```javascript Request theme={null}
              const response = await fetch('https://api.worldlabs.ai/marble/v1/worlds:generate', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'WLT-Api-Key': 'YOUR_API_KEY'
                },
                body: JSON.stringify({
                  display_name: 'Mystical Forest',
                  world_prompt: {
                    type: 'text',
                    text_prompt: 'A mystical forest with glowing mushrooms'
                  }
                })
              });

              const data = await response.json();

              console.log(data);
              ```

              ```python Request theme={null}
              import requests

              url = "https://api.worldlabs.ai/marble/v1/worlds:generate"

              payload = {
                  "display_name": "Mystical Forest",
                  "world_prompt": {
                      "type": "text",
                      "text_prompt": "A mystical forest with glowing mushrooms"
                  }
              }
              headers = {
                  "WLT-Api-Key": "YOUR_API_KEY",
                  "Content-Type": "application/json"
              }

              response = requests.post(url, json=payload, headers=headers)

              print(response.text)
              ```
            </CodeGroup>

            This will return an Operation object.

            <CodeGroup>
              ```json Response theme={null}
              {
                "operation_id": "20bffbb1-4ba7-453f-a116-93eaw1a6843e",
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:30:00Z",
                "expires_at": "2025-01-15T11:30:00Z",
                "done": false,
                "error": null,
                "metadata": null,
                "response": null
              }
              ```
            </CodeGroup>
          </Step>

          <Step>
            Poll the [`/marble/v1/operations/{operation_id}`](/api/reference/operations/get) endpoint until the operation is done.

            <CodeGroup>
              ```bash Request theme={null}
              curl -X GET 'https://api.worldlabs.ai/marble/v1/operations/20bffbb1-4ba7-453f-a116-93eaw1a6843e' \
                -H 'WLT-Api-Key: YOUR_API_KEY'
              ```

              ```javascript Request theme={null}
              const response = await fetch('https://api.worldlabs.ai/marble/v1/operations/20bffbb1-4ba7-453f-a116-93eaw1a6843e', {
                method: 'GET',
                headers: {
                  'WLT-Api-Key': 'YOUR_API_KEY'
                }
              });

              const data = await response.json();

              console.log(data);
              ```

              ```python Request theme={null}
              import requests

              url = "https://api.worldlabs.ai/marble/v1/operations/20bffbb1-4ba7-453f-a116-93eaw1a6843e"

              headers = {
                  "WLT-Api-Key": "YOUR_API_KEY"
              }

              response = requests.get(url, headers=headers)

              print(response.text)
              ```
            </CodeGroup>

            This will return an Operation object. If the operation is not done, it will return a `200` status code and the Operation object will have a `done` field set to `false`:

            <CodeGroup>
              ```json Response theme={null}
              {
                "operation_id": "20bffbb1-4ba7-453f-a116-93eaw1a6843e",
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:30:00Z",
                "expires_at": "2025-01-15T11:30:00Z",
                "done": false,
                "error": null,
                "metadata": {
                  "progress": { "status": "IN_PROGRESS", "description": "World generation in progress" },
                  "world_id": "dc2c65e4-68d3-4210-a01e-7a54cc9ded2a"
                },
                "response": null
              }
              ```
            </CodeGroup>

            World generation should take **about 5 minutes** to complete. Once the world is generated, the `done` field will be set to `true` and the `response` field will contain the generated World:

            <CodeGroup>
              ```json Response theme={null}
              {
                "operation_id": "20bffbb1-4ba7-453f-a116-93eab1a6843e",
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:35:00Z",
                "expires_at": "2025-01-15T11:30:00Z",
                "done": true,
                "error": null,
                "metadata": {
                  "progress": {
                    "status": "SUCCEEDED",
                    "description": "World generation completed successfully"
                  },
                  "world_id": "dc2c65e4-68d3-4210-a01e-7a54cc9ded2a"
                },
                "response": {
                  "id": "dc2c65e4-68d3-4210-a01e-7a54cc9ded2a",
                  "display_name": "",
                  "tags": null,
                  "world_marble_url": "https://marble.worldlabs.ai/world/dc2c65e4-68d3-4210-a01e-7a54cc9ded2a",
                  "assets": {
                    "caption": "The scene is a fantastical forest...",
                    "thumbnail_url": "<thumbnail_url>",
                    "splats": {
                      "spz_urls": {
                        "500k": "<500k_spz_url>",
                        "100k": "<100k_spz_url>",
                        "full_res": "<full_res_spz_url>"
                      }
                    },
                    "mesh": {
                      "collider_mesh_url": "<collider_mesh_url>"
                    },
                    "imagery": {
                      "pano_url": "<pano_url>"
                    }
                  },
                  "created_at": null,
                  "updated_at": null,
                  "permission": null,
                  "world_prompt": null,
                  "model": null
                }
              }
              ```
            </CodeGroup>

            <Note>
              The `response` field contains a snapshot of the World at the time the operation completed. This allows you to access the generated assets without making a separate API call. Note that some fields like `display_name`, `created_at`, `updated_at`, `world_prompt`, and `model` may be empty or null in this snapshot. Use the [`GET /marble/v1/worlds/{world_id}`](/api/reference/worlds/get) endpoint to fetch the complete, up-to-date world.
            </Note>

            You can view the generated world in Marble at `https://marble.worldlabs.ai/world/{world_id}`.
          </Step>

          <Step title="(Optional) Get the latest world">
            If you need to fetch the most up-to-date version of the world later, use the `world_id` to retrieve it.

            <CodeGroup>
              ```bash Request theme={null}
              curl -X GET 'https://api.worldlabs.ai/marble/v1/worlds/dc2c65e4-68d3-4210-a01e-7a54cc9ded2a' \
                -H 'WLT-Api-Key: YOUR_API_KEY'
              ```

              ```javascript Request theme={null}
              const response = await fetch('https://api.worldlabs.ai/marble/v1/worlds/dc2c65e4-68d3-4210-a01e-7a54cc9ded2a', {
                method: 'GET',
                headers: {
                  'WLT-Api-Key': 'YOUR_API_KEY'
                }
              });

              const data = await response.json();

              console.log(data);
              ```

              ```python Request theme={null}
              import requests

              url = "https://api.worldlabs.ai/marble/v1/worlds/dc2c65e4-68d3-4210-a01e-7a54cc9ded2a"

              headers = {
                  "WLT-Api-Key": "YOUR_API_KEY"
              }

              response = requests.get(url, headers=headers)

              print(response.text)
              ```
            </CodeGroup>

            This returns the latest version of the world:

            <CodeGroup>
              ```json Response theme={null}
              {
                "world": {
                  "id": "dc2c65e4-68d3-4210-a01e-7a54cc9ded2a",
                  "display_name": "Mystical Forest",
                  "tags": null,
                  "world_marble_url": "https://marble.worldlabs.ai/world/dc2c65e4-68d3-4210-a01e-7a54cc9ded2a",
                  "assets": {
                    "caption": "The scene is a fantastical forest...",
                    "thumbnail_url": "<thumbnail_url>",
                    "splats": {
                      "spz_urls": {
                        "500k": "<500k_spz_url>",
                        "full_res": "<full_res_spz_url>",
                        "100k": "<100k_spz_url>"
                      }
                    },
                    "mesh": {
                      "collider_mesh_url": "<collider_mesh_url>"
                    },
                    "imagery": {
                      "pano_url": "<pano_url>"
                    }
                  },
                  "created_at": "2025-01-15T10:30:00Z",
                  "updated_at": "2025-01-15T10:35:00Z",
                  "permission": null,
                  "world_prompt": {
                    "type": "text",
                    "text_prompt": "The scene is a fantastical forest..."
                  },
                  "model": "Marble 0.1-plus"
                }
              }
              ```
            </CodeGroup>

            The world object includes:

            * `assets.splats.spz_urls`: 3D Gaussian splat files in SPZ format (100k, 500k, and full resolution)
            * `assets.mesh.collider_mesh_url`: Collider mesh in GLB format
            * `assets.imagery.pano_url`: Panorama image
            * `assets.caption`: AI-generated description of the world
            * `assets.thumbnail_url`: Thumbnail image for the world
            * `world_prompt`: The prompt used to generate the world (may be recaptioned)
            * `model`: The model used for generation
          </Step>
        </Steps>
      </Tab>

      <Tab title="Image input">
        You can create a world from a single image using either a public URL or by uploading a local file.

        Recommended image formats: `jpg`, `jpeg`, `png`, `webp`.

        <Tabs>
          <Tab title="From URL">
            If your image is already hosted at a public URL, you can reference it directly.

            <Steps>
              <Step>
                Make a `POST` request to the [`/marble/v1/worlds:generate`](/api/reference/worlds/generate) endpoint with your image URL.

                <CodeGroup>
                  ```bash Request theme={null}
                  curl -X POST 'https://api.worldlabs.ai/marble/v1/worlds:generate' \
                    -H 'Content-Type: application/json' \
                    -H 'WLT-Api-Key: YOUR_API_KEY' \
                    -d '{
                      "display_name": "My Image World",
                      "world_prompt": {
                        "type": "image",
                        "image_prompt": {
                          "source": "uri",
                          "uri": "https://example.com/my-image.jpg"
                        },
                        "text_prompt": "A beautiful landscape"
                      }
                    }'
                  ```

                  ```javascript Request theme={null}
                  const response = await fetch('https://api.worldlabs.ai/marble/v1/worlds:generate', {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      'WLT-Api-Key': 'YOUR_API_KEY'
                    },
                    body: JSON.stringify({
                      display_name: 'My Image World',
                      world_prompt: {
                        type: 'image',
                        image_prompt: {
                          source: 'uri',
                          uri: 'https://example.com/my-image.jpg'
                        },
                        text_prompt: 'A beautiful landscape'
                      }
                    })
                  });

                  const data = await response.json();
                  console.log(data);
                  ```

                  ```python Request theme={null}
                  import requests

                  url = "https://api.worldlabs.ai/marble/v1/worlds:generate"

                  payload = {
                      "display_name": "My Image World",
                      "world_prompt": {
                          "type": "image",
                          "image_prompt": {
                              "source": "uri",
                              "uri": "https://example.com/my-image.jpg"
                          },
                          "text_prompt": "A beautiful landscape"
                      }
                  }
                  headers = {
                      "WLT-Api-Key": "YOUR_API_KEY",
                      "Content-Type": "application/json"
                  }

                  response = requests.post(url, json=payload, headers=headers)
                  print(response.text)
                  ```
                </CodeGroup>

                This returns an Operation object. Poll the operation as shown in the text input example until `done` is `true`. The completed operation's `response` field will contain the generated World.
              </Step>
            </Steps>
          </Tab>

          <Tab title="From local file">
            To use a local image file, first upload it as a media asset, then reference it in your generation request.

            <Steps>
              <Step title="Prepare the upload">
                Make a `POST` request to [`/marble/v1/media-assets:prepare_upload`](/api/reference/media-assets/prepare-upload) to get a signed upload URL.

                <CodeGroup>
                  ```bash Request theme={null}
                  curl -X POST 'https://api.worldlabs.ai/marble/v1/media-assets:prepare_upload' \
                    -H 'Content-Type: application/json' \
                    -H 'WLT-Api-Key: YOUR_API_KEY' \
                    -d '{
                      "file_name": "my-image.jpg",
                      "kind": "image",
                      "extension": "jpg"
                    }'
                  ```

                  ```javascript Request theme={null}
                  const response = await fetch('https://api.worldlabs.ai/marble/v1/media-assets:prepare_upload', {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      'WLT-Api-Key': 'YOUR_API_KEY'
                    },
                    body: JSON.stringify({
                      file_name: 'my-image.jpg',
                      kind: 'image',
                      extension: 'jpg'
                    })
                  });

                  const data = await response.json();
                  console.log(data);
                  ```

                  ```python Request theme={null}
                  import requests

                  url = "https://api.worldlabs.ai/marble/v1/media-assets:prepare_upload"

                  payload = {
                      "file_name": "my-image.jpg",
                      "kind": "image",
                      "extension": "jpg"
                  }
                  headers = {
                      "WLT-Api-Key": "YOUR_API_KEY",
                      "Content-Type": "application/json"
                  }

                  response = requests.post(url, json=payload, headers=headers)
                  print(response.text)
                  ```
                </CodeGroup>

                This returns the media asset and upload information:

                <CodeGroup>
                  ```json Response theme={null}
                  {
                    "media_asset": {
                      "id": "550e8400-e29b-41d4-a716-446655440000",
                      "file_name": "my-image.jpg",
                      "kind": "image",
                      "extension": "jpg",
                      "created_at": "2025-01-15T10:30:00Z",
                      "updated_at": null,
                      "metadata": null
                    },
                    "upload_info": {
                      "upload_url": "<signed_upload_url>",
                      "upload_method": "PUT",
                      "required_headers": {
                        "x-goog-content-length-range": "0,1048576000"
                      }
                    }
                  }
                  ```
                </CodeGroup>
              </Step>

              <Step title="Upload the file">
                Upload your image to the signed URL using the method and headers from the response.

                <CodeGroup>
                  ```bash Request theme={null}
                  curl -X PUT '<signed_upload_url>' \
                    -H 'x-goog-content-length-range: 0,1048576000' \
                    --data-binary '@/path/to/my-image.jpg'
                  ```

                  ```javascript Request theme={null}
                  const fs = require('fs');

                  const imageBuffer = fs.readFileSync('/path/to/my-image.jpg');

                  await fetch('<signed_upload_url>', {
                    method: 'PUT',
                    headers: upload_info.required_headers,
                    body: imageBuffer
                  });
                  ```

                  ```python Request theme={null}
                  import requests

                  with open('/path/to/my-image.jpg', 'rb') as f:
                      image_data = f.read()

                  requests.put(
                      '<signed_upload_url>',
                      headers=upload_info['required_headers'],
                      data=image_data
                  )
                  ```
                </CodeGroup>
              </Step>

              <Step title="Generate the world">
                Use the `media_asset_id` from Step 1 to generate a world.

                <CodeGroup>
                  ```bash Request theme={null}
                  curl -X POST 'https://api.worldlabs.ai/marble/v1/worlds:generate' \
                    -H 'Content-Type: application/json' \
                    -H 'WLT-Api-Key: YOUR_API_KEY' \
                    -d '{
                      "display_name": "My Image World",
                      "world_prompt": {
                        "type": "image",
                        "image_prompt": {
                          "source": "media_asset",
                          "media_asset_id": "550e8400-e29b-41d4-a716-446655440000"
                        },
                        "text_prompt": "A beautiful landscape"
                      }
                    }'
                  ```

                  ```javascript Request theme={null}
                  const response = await fetch('https://api.worldlabs.ai/marble/v1/worlds:generate', {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      'WLT-Api-Key': 'YOUR_API_KEY'
                    },
                    body: JSON.stringify({
                      display_name: 'My Image World',
                      world_prompt: {
                        type: 'image',
                        image_prompt: {
                          source: 'media_asset',
                          media_asset_id: '550e8400-e29b-41d4-a716-446655440000'
                        },
                        text_prompt: 'A beautiful landscape'
                      }
                    })
                  });

                  const data = await response.json();
                  console.log(data);
                  ```

                  ```python Request theme={null}
                  import requests

                  url = "https://api.worldlabs.ai/marble/v1/worlds:generate"

                  payload = {
                      "display_name": "My Image World",
                      "world_prompt": {
                          "type": "image",
                          "image_prompt": {
                              "source": "media_asset",
                              "media_asset_id": "550e8400-e29b-41d4-a716-446655440000"
                          },
                          "text_prompt": "A beautiful landscape"
                      }
                  }
                  headers = {
                      "WLT-Api-Key": "YOUR_API_KEY",
                      "Content-Type": "application/json"
                  }

                  response = requests.post(url, json=payload, headers=headers)
                  print(response.text)
                  ```
                </CodeGroup>

                This returns an Operation object. Poll the operation as shown in the text input example until `done` is `true`. The completed operation's `response` field will contain the generated World.
              </Step>
            </Steps>
          </Tab>
        </Tabs>

        <Note>
          The `text_prompt` field is optional. If omitted, a caption will be automatically generated from your image.
        </Note>

        <Note>
          Set `is_pano: true` in the `image_prompt` if your input image is a panorama.
        </Note>
      </Tab>

      <Tab title="Multi-image input">
        You can create a world from multiple images of the same scene, each with an optional azimuth (horizontal angle in degrees).

        Recommended image formats: `jpg`, `jpeg`, `png`, `webp`.

        <Tabs>
          <Tab title="From URLs">
            If your images are already hosted at public URLs, you can reference them directly.

            <Steps>
              <Step>
                Make a `POST` request to the [`/marble/v1/worlds:generate`](/api/reference/worlds/generate) endpoint with your image URLs and their azimuth positions.

                <CodeGroup>
                  ```bash Request theme={null}
                  curl -X POST 'https://api.worldlabs.ai/marble/v1/worlds:generate' \
                    -H 'Content-Type: application/json' \
                    -H 'WLT-Api-Key: YOUR_API_KEY' \
                    -d '{
                      "display_name": "My Multi-Image World",
                      "world_prompt": {
                        "type": "multi-image",
                        "multi_image_prompt": [
                          {
                            "azimuth": 0,
                            "content": {
                              "source": "uri",
                              "uri": "https://example.com/front.jpg"
                            }
                          },
                          {
                            "azimuth": 180,
                            "content": {
                              "source": "uri",
                              "uri": "https://example.com/back.jpg"
                            }
                          }
                        ],
                        "text_prompt": "A cozy living room"
                      }
                    }'
                  ```

                  ```javascript Request theme={null}
                  const response = await fetch('https://api.worldlabs.ai/marble/v1/worlds:generate', {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      'WLT-Api-Key': 'YOUR_API_KEY'
                    },
                    body: JSON.stringify({
                      display_name: 'My Multi-Image World',
                      world_prompt: {
                        type: 'multi-image',
                        multi_image_prompt: [
                          {
                            azimuth: 0,
                            content: {
                              source: 'uri',
                              uri: 'https://example.com/front.jpg'
                            }
                          },
                          {
                            azimuth: 180,
                            content: {
                              source: 'uri',
                              uri: 'https://example.com/back.jpg'
                            }
                          }
                        ],
                        text_prompt: 'A cozy living room'
                      }
                    })
                  });

                  const data = await response.json();
                  console.log(data);
                  ```

                  ```python Request theme={null}
                  import requests

                  url = "https://api.worldlabs.ai/marble/v1/worlds:generate"

                  payload = {
                      "display_name": "My Multi-Image World",
                      "world_prompt": {
                          "type": "multi-image",
                          "multi_image_prompt": [
                              {
                                  "azimuth": 0,
                                  "content": {
                                      "source": "uri",
                                      "uri": "https://example.com/front.jpg"
                                  }
                              },
                              {
                                  "azimuth": 180,
                                  "content": {
                                      "source": "uri",
                                      "uri": "https://example.com/back.jpg"
                                  }
                              }
                          ],
                          "text_prompt": "A cozy living room"
                      }
                  }
                  headers = {
                      "WLT-Api-Key": "YOUR_API_KEY",
                      "Content-Type": "application/json"
                  }

                  response = requests.post(url, json=payload, headers=headers)
                  print(response.text)
                  ```
                </CodeGroup>

                This returns an Operation object. Poll the operation as shown in the text input example until `done` is `true`. The completed operation's `response` field will contain the generated World.
              </Step>
            </Steps>
          </Tab>

          <Tab title="From local files">
            To use local image files, first upload each as a media asset, then reference them in your generation request.

            <Steps>
              <Step title="Prepare and upload each image">
                For each image, prepare the upload and upload the file as shown in the [image input example](#from-local-file).

                <CodeGroup>
                  ```bash Request theme={null}
                  # Prepare upload for first image
                  curl -X POST 'https://api.worldlabs.ai/marble/v1/media-assets:prepare_upload' \
                    -H 'Content-Type: application/json' \
                    -H 'WLT-Api-Key: YOUR_API_KEY' \
                    -d '{
                      "file_name": "front.jpg",
                      "kind": "image",
                      "extension": "jpg"
                    }'

                  # Upload the file to the returned upload_url
                  curl -X PUT '<upload_url>' \
                    -H 'Content-Type: image/jpeg' \
                    --data-binary '@/path/to/front.jpg'

                  # Repeat for each additional image
                  ```

                  ```javascript Request theme={null}
                  const fs = require('fs');

                  async function uploadImage(filePath, fileName) {
                    // Prepare upload
                    const prepareResponse = await fetch('https://api.worldlabs.ai/marble/v1/media-assets:prepare_upload', {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                        'WLT-Api-Key': 'YOUR_API_KEY'
                      },
                      body: JSON.stringify({
                        file_name: fileName,
                        kind: 'image',
                        extension: 'jpg'
                      })
                    });

                    const { media_asset, upload_info } = await prepareResponse.json();

                    // Upload file
                    const imageBuffer = fs.readFileSync(filePath);
                    await fetch(upload_info.upload_url, {
                      method: 'PUT',
                      headers: upload_info.required_headers,
                      body: imageBuffer
                    });

                    return media_asset.id;
                  }

                  const frontId = await uploadImage('/path/to/front.jpg', 'front.jpg');
                  const backId = await uploadImage('/path/to/back.jpg', 'back.jpg');
                  ```

                  ```python Request theme={null}
                  import requests

                  def upload_image(file_path, file_name):
                      # Prepare upload
                      prepare_response = requests.post(
                          'https://api.worldlabs.ai/marble/v1/media-assets:prepare_upload',
                          headers={
                              'WLT-Api-Key': 'YOUR_API_KEY',
                              'Content-Type': 'application/json'
                          },
                          json={
                              'file_name': file_name,
                              'kind': 'image',
                              'extension': 'jpg'
                          }
                      )

                      data = prepare_response.json()
                      media_asset = data['media_asset']
                      upload_info = data['upload_info']

                      # Upload file
                      with open(file_path, 'rb') as f:
                          requests.put(
                              upload_info['upload_url'],
                              headers=upload_info['required_headers'],
                              data=f.read()
                          )

                      return media_asset['id']

                  front_id = upload_image('/path/to/front.jpg', 'front.jpg')
                  back_id = upload_image('/path/to/back.jpg', 'back.jpg')
                  ```
                </CodeGroup>
              </Step>

              <Step title="Generate the world">
                Use the media asset IDs to generate a world.

                <CodeGroup>
                  ```bash Request theme={null}
                  curl -X POST 'https://api.worldlabs.ai/marble/v1/worlds:generate' \
                    -H 'Content-Type: application/json' \
                    -H 'WLT-Api-Key: YOUR_API_KEY' \
                    -d '{
                      "display_name": "My Multi-Image World",
                      "world_prompt": {
                        "type": "multi-image",
                        "multi_image_prompt": [
                          {
                            "azimuth": 0,
                            "content": {
                              "source": "media_asset",
                              "media_asset_id": "<front_image_id>"
                            }
                          },
                          {
                            "azimuth": 180,
                            "content": {
                              "source": "media_asset",
                              "media_asset_id": "<back_image_id>"
                            }
                          }
                        ],
                        "text_prompt": "A cozy living room"
                      }
                    }'
                  ```

                  ```javascript Request theme={null}
                  const response = await fetch('https://api.worldlabs.ai/marble/v1/worlds:generate', {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      'WLT-Api-Key': 'YOUR_API_KEY'
                    },
                    body: JSON.stringify({
                      display_name: 'My Multi-Image World',
                      world_prompt: {
                        type: 'multi-image',
                        multi_image_prompt: [
                          {
                            azimuth: 0,
                            content: {
                              source: 'media_asset',
                              media_asset_id: frontId
                            }
                          },
                          {
                            azimuth: 180,
                            content: {
                              source: 'media_asset',
                              media_asset_id: backId
                            }
                          }
                        ],
                        text_prompt: 'A cozy living room'
                      }
                    })
                  });

                  const data = await response.json();
                  console.log(data);
                  ```

                  ```python Request theme={null}
                  import requests

                  url = "https://api.worldlabs.ai/marble/v1/worlds:generate"

                  payload = {
                      "display_name": "My Multi-Image World",
                      "world_prompt": {
                          "type": "multi-image",
                          "multi_image_prompt": [
                              {
                                  "azimuth": 0,
                                  "content": {
                                      "source": "media_asset",
                                      "media_asset_id": front_id
                                  }
                              },
                              {
                                  "azimuth": 180,
                                  "content": {
                                      "source": "media_asset",
                                      "media_asset_id": back_id
                                  }
                              }
                          ],
                          "text_prompt": "A cozy living room"
                      }
                  }
                  headers = {
                      "WLT-Api-Key": "YOUR_API_KEY",
                      "Content-Type": "application/json"
                  }

                  response = requests.post(url, json=payload, headers=headers)
                  print(response.text)
                  ```
                </CodeGroup>

                This returns an Operation object. Poll the operation as shown in the text input example until `done` is `true`. The completed operation's `response` field will contain the generated World.
              </Step>
            </Steps>
          </Tab>
        </Tabs>

        <Note>
          The `azimuth` field specifies the horizontal angle (in degrees) where the image was taken. Use `0` for front, `90` for right, `180` for back, `270` for left.
        </Note>

        <Note>
          The `text_prompt` field is optional. If omitted, a caption will be automatically generated.
        </Note>
      </Tab>

      <Tab title="Video input">
        You can create a world from a video using either a public URL or by uploading a local file.

        Recommended video formats: `mp4`, `mov`, `mkv`.

        <Tabs>
          <Tab title="From URL">
            If your video is already hosted at a public URL, you can reference it directly.

            <Steps>
              <Step>
                Make a `POST` request to the [`/marble/v1/worlds:generate`](/api/reference/worlds/generate) endpoint with your video URL.

                <CodeGroup>
                  ```bash Request theme={null}
                  curl -X POST 'https://api.worldlabs.ai/marble/v1/worlds:generate' \
                    -H 'Content-Type: application/json' \
                    -H 'WLT-Api-Key: YOUR_API_KEY' \
                    -d '{
                      "display_name": "My Video World",
                      "world_prompt": {
                        "type": "video",
                        "video_prompt": {
                          "source": "uri",
                          "uri": "https://example.com/my-video.mp4"
                        },
                        "text_prompt": "A scenic mountain landscape"
                      }
                    }'
                  ```

                  ```javascript Request theme={null}
                  const response = await fetch('https://api.worldlabs.ai/marble/v1/worlds:generate', {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      'WLT-Api-Key': 'YOUR_API_KEY'
                    },
                    body: JSON.stringify({
                      display_name: 'My Video World',
                      world_prompt: {
                        type: 'video',
                        video_prompt: {
                          source: 'uri',
                          uri: 'https://example.com/my-video.mp4'
                        },
                        text_prompt: 'A scenic mountain landscape'
                      }
                    })
                  });

                  const data = await response.json();
                  console.log(data);
                  ```

                  ```python Request theme={null}
                  import requests

                  url = "https://api.worldlabs.ai/marble/v1/worlds:generate"

                  payload = {
                      "display_name": "My Video World",
                      "world_prompt": {
                          "type": "video",
                          "video_prompt": {
                              "source": "uri",
                              "uri": "https://example.com/my-video.mp4"
                          },
                          "text_prompt": "A scenic mountain landscape"
                      }
                  }
                  headers = {
                      "WLT-Api-Key": "YOUR_API_KEY",
                      "Content-Type": "application/json"
                  }

                  response = requests.post(url, json=payload, headers=headers)
                  print(response.text)
                  ```
                </CodeGroup>

                This returns an Operation object. Poll the operation as shown in the text input example until `done` is `true`. The completed operation's `response` field will contain the generated World.
              </Step>
            </Steps>
          </Tab>

          <Tab title="From local file">
            To use a local video file, first upload it as a media asset, then reference it in your generation request.

            <Steps>
              <Step title="Prepare the upload">
                Make a `POST` request to [`/marble/v1/media-assets:prepare_upload`](/api/reference/media-assets/prepare-upload) to get a signed upload URL.

                <CodeGroup>
                  ```bash Request theme={null}
                  curl -X POST 'https://api.worldlabs.ai/marble/v1/media-assets:prepare_upload' \
                    -H 'Content-Type: application/json' \
                    -H 'WLT-Api-Key: YOUR_API_KEY' \
                    -d '{
                      "file_name": "my-video.mp4",
                      "kind": "video",
                      "extension": "mp4"
                    }'
                  ```

                  ```javascript Request theme={null}
                  const response = await fetch('https://api.worldlabs.ai/marble/v1/media-assets:prepare_upload', {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      'WLT-Api-Key': 'YOUR_API_KEY'
                    },
                    body: JSON.stringify({
                      file_name: 'my-video.mp4',
                      kind: 'video',
                      extension: 'mp4'
                    })
                  });

                  const data = await response.json();
                  console.log(data);
                  ```

                  ```python Request theme={null}
                  import requests

                  url = "https://api.worldlabs.ai/marble/v1/media-assets:prepare_upload"

                  payload = {
                      "file_name": "my-video.mp4",
                      "kind": "video",
                      "extension": "mp4"
                  }
                  headers = {
                      "WLT-Api-Key": "YOUR_API_KEY",
                      "Content-Type": "application/json"
                  }

                  response = requests.post(url, json=payload, headers=headers)
                  print(response.text)
                  ```
                </CodeGroup>

                This returns the media asset and upload information:

                <CodeGroup>
                  ```json Response theme={null}
                  {
                    "media_asset": {
                      "id": "550e8400-e29b-41d4-a716-446655440000",
                      "file_name": "my-video.mp4",
                      "kind": "video",
                      "extension": "mp4",
                      "created_at": "2025-01-15T10:30:00Z",
                      "updated_at": null,
                      "metadata": null
                    },
                    "upload_info": {
                      "upload_url": "<signed_upload_url>",
                      "upload_method": "PUT",
                      "required_headers": {
                        "x-goog-content-length-range": "0,1048576000"
                      }
                    }
                  }
                  ```
                </CodeGroup>
              </Step>

              <Step title="Upload the file">
                Upload your video to the signed URL using the method and headers from the response.

                <CodeGroup>
                  ```bash Request theme={null}
                  curl -X PUT '<signed_upload_url>' \
                    -H 'x-goog-content-length-range: 0,1048576000' \
                    --data-binary '@/path/to/my-video.mp4'
                  ```

                  ```javascript Request theme={null}
                  const fs = require('fs');

                  const videoBuffer = fs.readFileSync('/path/to/my-video.mp4');

                  await fetch('<signed_upload_url>', {
                    method: 'PUT',
                    headers: upload_info.required_headers,
                    body: videoBuffer
                  });
                  ```

                  ```python Request theme={null}
                  import requests

                  with open('/path/to/my-video.mp4', 'rb') as f:
                      video_data = f.read()

                  requests.put(
                      '<signed_upload_url>',
                      headers=upload_info['required_headers'],
                      data=video_data
                  )
                  ```
                </CodeGroup>
              </Step>

              <Step title="Generate the world">
                Use the `media_asset_id` from Step 1 to generate a world.

                <CodeGroup>
                  ```bash Request theme={null}
                  curl -X POST 'https://api.worldlabs.ai/marble/v1/worlds:generate' \
                    -H 'Content-Type: application/json' \
                    -H 'WLT-Api-Key: YOUR_API_KEY' \
                    -d '{
                      "display_name": "My Video World",
                      "world_prompt": {
                        "type": "video",
                        "video_prompt": {
                          "source": "media_asset",
                          "media_asset_id": "550e8400-e29b-41d4-a716-446655440000"
                        },
                        "text_prompt": "A scenic mountain landscape"
                      }
                    }'
                  ```

                  ```javascript Request theme={null}
                  const response = await fetch('https://api.worldlabs.ai/marble/v1/worlds:generate', {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      'WLT-Api-Key': 'YOUR_API_KEY'
                    },
                    body: JSON.stringify({
                      display_name: 'My Video World',
                      world_prompt: {
                        type: 'video',
                        video_prompt: {
                          source: 'media_asset',
                          media_asset_id: '550e8400-e29b-41d4-a716-446655440000'
                        },
                        text_prompt: 'A scenic mountain landscape'
                      }
                    })
                  });

                  const data = await response.json();
                  console.log(data);
                  ```

                  ```python Request theme={null}
                  import requests

                  url = "https://api.worldlabs.ai/marble/v1/worlds:generate"

                  payload = {
                      "display_name": "My Video World",
                      "world_prompt": {
                          "type": "video",
                          "video_prompt": {
                              "source": "media_asset",
                              "media_asset_id": "550e8400-e29b-41d4-a716-446655440000"
                          },
                          "text_prompt": "A scenic mountain landscape"
                      }
                  }
                  headers = {
                      "WLT-Api-Key": "YOUR_API_KEY",
                      "Content-Type": "application/json"
                  }

                  response = requests.post(url, json=payload, headers=headers)
                  print(response.text)
                  ```
                </CodeGroup>

                This returns an Operation object. Poll the operation as shown in the text input example until `done` is `true`. The completed operation's `response` field will contain the generated World.
              </Step>
            </Steps>
          </Tab>
        </Tabs>

        <Note>
          The `text_prompt` field is optional. If omitted, a caption will be automatically generated from your video.
        </Note>
      </Tab>
    </Tabs>
  </Step>
</Steps>


# Pricing
Source: https://docs.worldlabs.ai/api/pricing

Understanding API usage and credits

## Credits

<Warning>
  World API billing is separate from Marble web app billing.

  * Credits purchased for the Marble app at [marble.worldlabs.ai](marble.worldlabs.ai) CANNOT be used with the API
  * API usage requires credits purchased through the World Labs Platform at [platform.worldlabs.ai](platform.worldlabs.ai)

  If you plan to use the API, make sure you purchase credits on the World Labs Platform, not in the Marble app.
</Warning>

The World Labs API uses a credit-based pricing model.

You may purchase credits at a fixed rate of \$1.00 USD per 1,250 credits through the [World Labs Platform](https://platform.worldlabs.ai/billing). The minimum purchase is 6,250 credits or \$5.00 USD.

API credits do not expire.

### Auto-refill

You may enable auto-refill to avoid service interruptions by automatically purchasing credits when your balance is low.

On the [billing page](https://platform.worldlabs.ai/billing), you may enable and configure auto-refill once you have a payment method on file.

You may configure the threshold at which auto-refill is triggered, as well as the target balance to refill to.

<Warning>
  Note that when auto-refill is triggered, your balance will not settle at the target balance. This is because the refill is applied before the cost of the API request is deducted from your balance.

  For example, assume your threshold is 10,000 credits and your target balance is 20,000 credits, and you have a balance of 10,000 credits.

  1. You make an API request that costs 1,500 credits. We would observe that your balance would drop to 8,500 credits, which is below your threshold.
  2. The auto-refill would then be triggered and you would be charged to bring your balance to 20,000 credits.
  3. Finally, your balance would drop to 18,500 credits to charge for the API request.
</Warning>

## Usage events

Credits are consumed as you use the API.

API requests may map to one or more usage events, and each usage event may have its own cost in credits associated with it. The total cost of an API request is the sum of the costs of all the usage events it maps to. The cost of each usage event is determined largely by the compute resources required to complete the underlying operation.

You may view your usage event history in the [usage page](https://platform.worldlabs.ai/usage).

Note that not all API requests consume credits, such as API key creation, media asset upload and management, and Operation polling.

### World generation pricing

Generating a world using the [World Generation API](/api/reference/worlds/generate) is the most common API request. However, the number of usage events and the cost of generating a world depends on the input type.

The World Generation API requires a panorama image (pano) to convert into a 3D world, so it will first generate a pano from your input if a pano is not provided. As a result, a World Generation API request often includes two usage events:

1. Pano generation (if needed)
2. World generation (from pano)

The **world generation** usage event is billed at **1,500 credits** for **Standard / Marble 0.1-plus**, and **150 credits** for **Draft / Marble 0.1-mini**.

Depending on your input type, you may also incur a **pano generation** usage event. If you generate from an existing pano, there is no pano generation step, so there is no additional cost.

#### Pricing (Standard / Marble 0.1-plus)

| Input type       | Pano generation | World generation | Total |
| ---------------- | --------------: | ---------------: | ----: |
| Image (pano)     |               0 |            1,500 | 1,500 |
| Text             |              80 |            1,500 | 1,580 |
| Image (non-pano) |              80 |            1,500 | 1,580 |
| Multi-image      |             100 |            1,500 | 1,600 |
| Video            |             100 |            1,500 | 1,600 |

#### Pricing (Draft / Marble 0.1-mini)

| Input type       | Pano generation | World generation | Total |
| ---------------- | --------------: | ---------------: | ----: |
| Image (pano)     |               0 |              150 |   150 |
| Text             |              80 |              150 |   230 |
| Image (non-pano) |              80 |              150 |   230 |
| Multi-image      |             100 |              150 |   250 |
| Video            |             100 |              150 |   250 |


# Rate limits
Source: https://docs.worldlabs.ai/api/rate-limits

Rate limits and time estimates for world generation

## Rate limits

Each API user is limited to **about 6 world generation requests per minute**. This is to ensure fair usage and prevent abuse.

Note that this limit is not per API key, but rather per API user.

Usage is tracked in a rolling window, and the limit is not guaranteed to be exact. For example, you may very occasionally find you can only make 5 requests in a 1 minute window.

### How to handle rate limits

If you exceed the rate limit, you will receive a 429 error. You can retry your request after the rate limit has been reset.

### Time estimates

Each world generation will take about 5 minutes to complete.


# Get media asset
Source: https://docs.worldlabs.ai/api/reference/media-assets/get

GET /marble/v1/media-assets/{media_asset_id}
Get a media asset by ID.

Retrieves metadata for a previously created media asset.

Args:
    media_asset_id: The media asset identifier.

Returns:
    MediaAsset object with media_asset_id, file_name, extension, kind,
    metadata, created_at, and updated_at.

Raises:
    HTTPException: 404 if not found



# Prepare media asset upload
Source: https://docs.worldlabs.ai/api/reference/media-assets/prepare-upload

POST /marble/v1/media-assets:prepare_upload
Prepare a media asset upload for use in world generation.

This API endpoint creates a media asset record and returns a signed upload URL.
Use this workflow to upload images or videos that you want to reference in world
generation requests.

## Workflow

1. **Prepare Upload** (this endpoint): Get a `media_asset_id` and `upload_url`
2. **Upload File**: Use the signed URL to upload your file
3. **Generate World**: Reference the `media_asset_id` in `/worlds:generate` with
   source type "media_asset"

## Request Parameters

- `file_name`: Your file's name (e.g., "landscape.jpg")
- `extension`: File extension without dot (e.g., "jpg", "png", "mp4")
- `kind`: Either "image" or "video"
- `metadata`: Optional custom metadata object

## Response

Returns a `MediaAssetPrepareUploadResponse` containing:

- `media_asset`: Object with `media_asset_id` (use this in world generation)
- `upload_info`: Object with `upload_url`, `required_headers`, and `curl_example`

## Uploading Your File

Use the returned `upload_url` and `required_headers` to upload your file:

```bash
curl --request PUT \
  --url <upload_url> \
  --header "Content-Type: <content-type>" \
  --header "<header-name>: <header-value>" \
  --upload-file /path/to/your/file
```

Replace:
- `<upload_url>`: The `upload_url` from the response
- `<content-type>`: MIME type (e.g., `image/png`, `image/jpeg`, `video/mp4`)
- `<header-name>: <header-value>`: Each header from `required_headers`
- `/path/to/your/file`: Path to your local file

## Example Usage in World Generation

After uploading, use the `media_asset_id` in a world generation request:

```json
{
  "world_prompt": {
    "type": "image",
    "image_prompt": {
      "source": "media_asset",
      "media_asset_id": "<your-media-asset-id>"
    }
  }
}
```



# OpenAPI spec
Source: https://docs.worldlabs.ai/api/reference/openapi

View the OpenAPI specification file

We use an OpenAPI spec to generate endpoint documentation. You can consume the
spec directly or browse API reference pages.

<Accordion title="World API v1 OpenAPI spec">
  ````yaml theme={null}
  components:
    schemas:
      Content:
        description: 'Represents content (media, text, images) that can be stored inline
          or via URL.


          Supports both direct data storage (up to 10MB) and URL references (up to 20MB).'
        properties:
          data_base64:
            anyOf:
            - type: string
            - type: 'null'
            title: Data Base64
          extension:
            anyOf:
            - type: string
            - type: 'null'
            description: File extension without dot
            examples:
            - jpg
            - png
            - pdf
            - txt
            title: Extension
          uri:
            anyOf:
            - type: string
            - type: 'null'
            title: Uri
        title: Content
        type: object
      DataBase64Reference:
        description: Reference to content via base64-encoded data.
        properties:
          data_base64:
            description: Base64-encoded content data
            title: Data Base64
            type: string
          extension:
            anyOf:
            - type: string
            - type: 'null'
            description: File extension without dot (e.g., 'jpg', 'png')
            title: Extension
          source:
            const: data_base64
            default: data_base64
            title: Source
            type: string
        required:
        - data_base64
        title: DataBase64Reference
        type: object
      DepthPanoPrompt:
        description: For models conditioned on a depth pano and text.
        properties:
          depth_pano_image:
            $ref: '#/components/schemas/Content'
          text_prompt:
            anyOf:
            - type: string
            - type: 'null'
            title: Text Prompt
          type:
            const: depth-pano
            default: depth-pano
            title: Type
            type: string
          z_max:
            title: Z Max
            type: number
          z_min:
            title: Z Min
            type: number
        required:
        - depth_pano_image
        - z_min
        - z_max
        title: DepthPanoPrompt
        type: object
      GenerateWorldResponse:
        description: Response from world generation endpoint.
        properties:
          created_at:
            anyOf:
            - format: date-time
              type: string
            - type: 'null'
            description: Creation timestamp
            title: Created At
          done:
            description: True if the operation is completed
            title: Done
            type: boolean
          error:
            anyOf:
            - $ref: '#/components/schemas/OperationError'
            - type: 'null'
            description: Error information if the operation failed
          expires_at:
            anyOf:
            - format: date-time
              type: string
            - type: 'null'
            description: Expiration timestamp
            title: Expires At
          metadata:
            anyOf:
            - type: object
            - type: 'null'
            description: Service-specific metadata, such as progress percentage
            title: Metadata
          operation_id:
            description: Operation identifier
            title: Operation Id
            type: string
          response:
            anyOf:
            - {}
            - type: 'null'
            description: Result payload when done=true and no error. Structure depends
              on operation type.
            title: Response
          updated_at:
            anyOf:
            - format: date-time
              type: string
            - type: 'null'
            description: Last update timestamp
            title: Updated At
        required:
        - operation_id
        - done
        title: GenerateWorldResponse
        type: object
      GetOperationResponse_World_:
        properties:
          created_at:
            anyOf:
            - format: date-time
              type: string
            - type: 'null'
            description: Creation timestamp
            title: Created At
          done:
            description: True if the operation is completed
            title: Done
            type: boolean
          error:
            anyOf:
            - $ref: '#/components/schemas/OperationError'
            - type: 'null'
            description: Error information if the operation failed
          expires_at:
            anyOf:
            - format: date-time
              type: string
            - type: 'null'
            description: Expiration timestamp
            title: Expires At
          metadata:
            anyOf:
            - type: object
            - type: 'null'
            description: Service-specific metadata, such as progress percentage
            title: Metadata
          operation_id:
            description: Operation identifier
            title: Operation Id
            type: string
          response:
            anyOf:
            - $ref: '#/components/schemas/World'
            - type: 'null'
            description: Result payload when done=true and no error. Structure depends
              on operation type.
          updated_at:
            anyOf:
            - format: date-time
              type: string
            - type: 'null'
            description: Last update timestamp
            title: Updated At
        required:
        - operation_id
        - done
        title: GetOperationResponse[World]
        type: object
      HTTPValidationError:
        properties:
          detail:
            items:
              $ref: '#/components/schemas/ValidationError'
            title: Detail
            type: array
        title: HTTPValidationError
        type: object
      ImagePrompt:
        description: 'Image-to-world generation.


          Generates a world from an image. text_prompt is optional - if not provided,

          it will be generated via recaptioning.


          Recommended image formats: jpg, jpeg, png, webp.'
        properties:
          disable_recaption:
            anyOf:
            - type: boolean
            - type: 'null'
            description: If True, use text_prompt as-is without recaptioning
            title: Disable Recaption
          image_prompt:
            description: Image content for world generation
            discriminator:
              mapping:
                data_base64: '#/components/schemas/DataBase64Reference'
                media_asset: '#/components/schemas/MediaAssetReference'
                uri: '#/components/schemas/UriReference'
              propertyName: source
            oneOf:
            - $ref: '#/components/schemas/MediaAssetReference'
            - $ref: '#/components/schemas/UriReference'
            - $ref: '#/components/schemas/DataBase64Reference'
            title: Image Prompt
          is_pano:
            anyOf:
            - type: boolean
            - type: 'null'
            description: Whether the provided image is already a panorama
            title: Is Pano
          text_prompt:
            anyOf:
            - type: string
            - type: 'null'
            description: Optional text guidance (auto-generated if not provided)
            title: Text Prompt
          type:
            const: image
            default: image
            title: Type
            type: string
        required:
        - image_prompt
        title: ImagePrompt
        type: object
      ImageryAssets:
        description: Imagery asset URLs.
        properties:
          pano_url:
            anyOf:
            - type: string
            - type: 'null'
            description: Panorama image URL
            title: Pano Url
        title: ImageryAssets
        type: object
      InpaintPanoPrompt:
        description: For models that inpaint the masked portion of a pano image.
        properties:
          pano_image:
            $ref: '#/components/schemas/Content'
          pano_mask:
            $ref: '#/components/schemas/Content'
          text_prompt:
            anyOf:
            - type: string
            - type: 'null'
            title: Text Prompt
          type:
            const: inpaint-pano
            default: inpaint-pano
            title: Type
            type: string
        required:
        - pano_image
        - pano_mask
        title: InpaintPanoPrompt
        type: object
      ListWorldsRequest:
        description: Request to list API-generated worlds with optional filters.
        examples:
        - model: Marble 0.1-plus
          page_size: 20
          sort_by: created_at
          status: SUCCEEDED
        - is_public: true
          page_size: 50
          sort_by: created_at
          status: SUCCEEDED
          tags:
          - fantasy
          - nature
        - created_after: '2024-01-01T00:00:00Z'
          created_before: '2024-12-31T23:59:59Z'
          page_size: 100
          sort_by: created_at
        - is_public: false
          model: Marble 0.1-mini
          page_size: 30
          tags:
          - landscape
        properties:
          created_after:
            anyOf:
            - format: date-time
              type: string
            - type: 'null'
            description: Filter worlds created after this timestamp (inclusive)
            title: Created After
          created_before:
            anyOf:
            - format: date-time
              type: string
            - type: 'null'
            description: Filter worlds created before this timestamp (exclusive)
            title: Created Before
          is_public:
            anyOf:
            - type: boolean
            - type: 'null'
            description: Filter by public visibility (true=public, false=private)
            title: Is Public
          model:
            anyOf:
            - enum:
              - Marble 0.1-mini
              - Marble 0.1-plus
              type: string
            - type: 'null'
            description: Filter by model used for generation
            title: Model
          page_size:
            default: 20
            description: Number of results per page (1-100)
            maximum: 100.0
            minimum: 1.0
            title: Page Size
            type: integer
          page_token:
            anyOf:
            - type: string
            - type: 'null'
            description: Cursor token for pagination (opaque base64 string from previous
              response)
            title: Page Token
          sort_by:
            default: created_at
            description: Sort results by created_at or updated_at
            enum:
            - created_at
            - updated_at
            title: Sort By
            type: string
          status:
            anyOf:
            - enum:
              - SUCCEEDED
              - PENDING
              - FAILED
              - RUNNING
              type: string
            - type: 'null'
            description: Filter by world status
            title: Status
          tags:
            anyOf:
            - items:
                type: string
              type: array
            - type: 'null'
            description: Filter by tags (returns worlds with ANY of these tags)
            title: Tags
        title: ListWorldsRequest
        type: object
      ListWorldsResponse:
        description: Response containing a list of API-generated worlds.
        properties:
          next_page_token:
            anyOf:
            - type: string
            - type: 'null'
            description: Token for fetching the next page of results
            title: Next Page Token
          worlds:
            description: List of worlds
            items:
              $ref: '#/components/schemas/World'
            title: Worlds
            type: array
        required:
        - worlds
        title: ListWorldsResponse
        type: object
      MediaAsset:
        description: 'A user-uploaded media asset stored in managed storage.


          MediaAssets can be images, videos, or binary blobs that are used

          as input to world generation.'
        properties:
          created_at:
            description: Creation timestamp
            format: date-time
            title: Created At
            type: string
          extension:
            anyOf:
            - type: string
            - type: 'null'
            description: File extension without dot
            examples:
            - mp4
            - png
            - jpg
            title: Extension
          file_name:
            description: File name
            title: File Name
            type: string
          kind:
            $ref: '#/components/schemas/MediaAssetKind'
            description: High-level media type
            examples:
            - image
            - video
          media_asset_id:
            description: Server-generated media asset identifier
            title: Media Asset Id
            type: string
          metadata:
            anyOf:
            - type: object
            - type: 'null'
            description: Optional application-specific metadata
            title: Metadata
          updated_at:
            anyOf:
            - format: date-time
              type: string
            - type: 'null'
            description: Last update timestamp
            title: Updated At
        required:
        - media_asset_id
        - file_name
        - kind
        - created_at
        title: MediaAsset
        type: object
      MediaAssetKind:
        description: High-level media asset type.
        enum:
        - image
        - video
        title: MediaAssetKind
        type: string
      MediaAssetPrepareUploadRequest:
        description: Request to prepare a media asset upload.
        properties:
          extension:
            anyOf:
            - type: string
            - type: 'null'
            description: File extension without dot
            examples:
            - mp4
            - png
            - jpg
            title: Extension
          file_name:
            description: File name
            title: File Name
            type: string
          kind:
            $ref: '#/components/schemas/MediaAssetKind'
            description: High-level media type
            examples:
            - image
            - video
          metadata:
            anyOf:
            - type: object
            - type: 'null'
            description: Optional application-specific metadata
            title: Metadata
        required:
        - file_name
        - kind
        title: MediaAssetPrepareUploadRequest
        type: object
      MediaAssetPrepareUploadResponse:
        description: Response from preparing a media asset upload.
        properties:
          media_asset:
            $ref: '#/components/schemas/MediaAsset'
            description: The created media asset
          upload_info:
            $ref: '#/components/schemas/UploadUrlInfo'
            description: Upload URL information
        required:
        - media_asset
        - upload_info
        title: MediaAssetPrepareUploadResponse
        type: object
      MediaAssetReference:
        description: Reference to a previously uploaded MediaAsset.
        properties:
          media_asset_id:
            description: ID of a MediaAsset resource previously created and marked READY
            title: Media Asset Id
            type: string
          source:
            const: media_asset
            default: media_asset
            title: Source
            type: string
        required:
        - media_asset_id
        title: MediaAssetReference
        type: object
      MeshAssets:
        description: Mesh asset URLs.
        properties:
          collider_mesh_url:
            anyOf:
            - type: string
            - type: 'null'
            description: Collider mesh URL
            title: Collider Mesh Url
        title: MeshAssets
        type: object
      OperationError:
        description: Error information for a failed operation.
        properties:
          code:
            anyOf:
            - type: integer
            - type: 'null'
            description: Error code
            title: Code
          message:
            anyOf:
            - type: string
            - type: 'null'
            description: Error message
            title: Message
        title: OperationError
        type: object
      Permission:
        description: Access control permissions for a resource.
        properties:
          allowed_readers:
            items:
              type: string
            title: Allowed Readers
            type: array
          allowed_writers:
            items:
              type: string
            title: Allowed Writers
            type: array
          public:
            default: false
            title: Public
            type: boolean
        title: Permission
        type: object
      Prompt:
        description: 'For world models generating a world from a single image (+ text).

          Images can be generated using the :image-generation method.

          If no text prompt is provided, it will be generated via recaption.'
        properties:
          image_prompt:
            $ref: '#/components/schemas/Content'
          is_pano:
            default: false
            title: Is Pano
            type: boolean
          text_prompt:
            anyOf:
            - type: string
            - type: 'null'
            title: Text Prompt
          type:
            const: image
            default: image
            title: Type
            type: string
        required:
        - image_prompt
        title: Prompt
        type: object
      SplatAssets:
        description: Gaussian splat asset URLs.
        properties:
          spz_urls:
            anyOf:
            - additionalProperties:
                type: string
              type: object
            - type: 'null'
            description: URLs for SPZ format Gaussian splat files
            title: Spz Urls
        title: SplatAssets
        type: object
      UploadUrlInfo:
        description: Information required to upload raw bytes directly to storage.
        properties:
          curl_example:
            anyOf:
            - type: string
            - type: 'null'
            description: Optional curl example for convenience
            title: Curl Example
          required_headers:
            anyOf:
            - additionalProperties:
                type: string
              type: object
            - type: 'null'
            description: Headers that MUST be included when uploading (e.g. Content-Type)
            title: Required Headers
          upload_method:
            description: Upload method
            title: Upload Method
            type: string
          upload_url:
            description: Signed URL for uploading bytes via PUT
            title: Upload Url
            type: string
        required:
        - upload_url
        - upload_method
        title: UploadUrlInfo
        type: object
      UriReference:
        description: Reference to content via a publicly accessible URL.
        properties:
          source:
            const: uri
            default: uri
            title: Source
            type: string
          uri:
            description: Publicly accessible URL pointing to the media
            title: Uri
            type: string
        required:
        - uri
        title: UriReference
        type: object
      ValidationError:
        properties:
          loc:
            items:
              anyOf:
              - type: string
              - type: integer
            title: Location
            type: array
          msg:
            title: Message
            type: string
          type:
            title: Error Type
            type: string
        required:
        - loc
        - msg
        - type
        title: ValidationError
        type: object
      World:
        description: A generated world, including asset URLs.
        properties:
          assets:
            anyOf:
            - $ref: '#/components/schemas/WorldAssets'
            - type: 'null'
            description: Generated world assets
          created_at:
            anyOf:
            - format: date-time
              type: string
            - type: 'null'
            description: Creation timestamp
            title: Created At
          display_name:
            description: Display name
            title: Display Name
            type: string
          model:
            anyOf:
            - type: string
            - type: 'null'
            description: Model used for generation
            title: Model
          permission:
            anyOf:
            - $ref: '#/components/schemas/Permission'
            - type: 'null'
            description: Access control permissions for the world
          tags:
            anyOf:
            - items:
                type: string
              type: array
            - type: 'null'
            description: Tags associated with the world
            title: Tags
          updated_at:
            anyOf:
            - format: date-time
              type: string
            - type: 'null'
            description: Last update timestamp
            title: Updated At
          world_id:
            description: World identifier
            title: World Id
            type: string
          world_marble_url:
            description: World Marble URL
            title: World Marble Url
            type: string
          world_prompt:
            anyOf:
            - discriminator:
                mapping:
                  depth-pano: '#/components/schemas/DepthPanoPrompt'
                  image: '#/components/schemas/Prompt'
                  inpaint-pano: '#/components/schemas/InpaintPanoPrompt'
                  multi-image: '#/components/schemas/MultiImagePrompt-Output'
                  text: '#/components/schemas/WorldTextPrompt-Output'
                  video: '#/components/schemas/VideoPrompt-Output'
                propertyName: type
              oneOf:
              - $ref: '#/components/schemas/wlt__marble__v1__schema__api_schema__WorldTextPrompt'
              - $ref: '#/components/schemas/Prompt'
              - $ref: '#/components/schemas/wlt__marble__v1__schema__api_schema__MultiImagePrompt'
              - $ref: '#/components/schemas/wlt__marble__v1__schema__api_schema__VideoPrompt'
              - $ref: '#/components/schemas/DepthPanoPrompt'
              - $ref: '#/components/schemas/InpaintPanoPrompt'
            - type: 'null'
            description: World prompt
            title: World Prompt
        required:
        - world_id
        - display_name
        - world_marble_url
        title: World
        type: object
      WorldAssets:
        description: Downloadable outputs of world generation.
        properties:
          caption:
            anyOf:
            - type: string
            - type: 'null'
            description: AI-generated description of the world
            title: Caption
          imagery:
            anyOf:
            - $ref: '#/components/schemas/ImageryAssets'
            - type: 'null'
            description: Imagery assets
          mesh:
            anyOf:
            - $ref: '#/components/schemas/MeshAssets'
            - type: 'null'
            description: Mesh assets
          splats:
            anyOf:
            - $ref: '#/components/schemas/SplatAssets'
            - type: 'null'
            description: Gaussian splat assets
          thumbnail_url:
            anyOf:
            - type: string
            - type: 'null'
            description: Thumbnail URL for the world
            title: Thumbnail Url
        title: WorldAssets
        type: object
      WorldsGenerateRequest:
        description: Request to generate a world from text, image, multi-image, or video
          input.
        examples:
        - display_name: Enchanted Forest
          model: Marble 0.1-plus
          permission:
            public: false
          seed: 42
          tags:
          - fantasy
          - nature
          world_prompt:
            text_prompt: A mystical forest with glowing mushrooms
            type: text
        - display_name: World from Image
          model: Marble 0.1-mini
          world_prompt:
            image_prompt:
              source: uri
              uri: https://example.com/my-image.jpg
            is_pano: false
            text_prompt: A beautiful landscape
            type: image
        - permission:
            public: true
          world_prompt:
            type: video
            video_prompt:
              media_asset_id: 550e8400e29b41d4a716446655440000
              source: media_asset
        - display_name: World from Multiple Images
          model: Marble 0.1-plus
          world_prompt:
            multi_image_prompt:
            - azimuth: 0
              content:
                source: uri
                uri: https://example.com/image1.jpg
            - azimuth: 180
              content:
                source: uri
                uri: https://example.com/image2.jpg
            type: multi-image
        properties:
          display_name:
            anyOf:
            - type: string
            - type: 'null'
            description: Optional display name
            title: Display Name
          model:
            default: Marble 0.1-plus
            description: The model to use for generation
            enum:
            - Marble 0.1-mini
            - Marble 0.1-plus
            title: Model
            type: string
          permission:
            $ref: '#/components/schemas/Permission'
            default:
              allowed_readers: []
              allowed_writers: []
              public: false
            description: The permission for the world
          seed:
            anyOf:
            - minimum: 0.0
              type: integer
            - type: 'null'
            description: Random seed for generation
            title: Seed
          tags:
            anyOf:
            - items:
                type: string
              type: array
            - type: 'null'
            description: Optional tags for the world
            title: Tags
          world_prompt:
            description: The prompt specifying how to generate the world
            discriminator:
              mapping:
                image: '#/components/schemas/ImagePrompt'
                multi-image: '#/components/schemas/MultiImagePrompt-Input'
                text: '#/components/schemas/WorldTextPrompt-Input'
                video: '#/components/schemas/VideoPrompt-Input'
              propertyName: type
            oneOf:
            - $ref: '#/components/schemas/wlt__marble__v1__public_api__schemas__prompts__WorldTextPrompt'
            - $ref: '#/components/schemas/ImagePrompt'
            - $ref: '#/components/schemas/wlt__marble__v1__public_api__schemas__prompts__MultiImagePrompt'
            - $ref: '#/components/schemas/wlt__marble__v1__public_api__schemas__prompts__VideoPrompt'
            title: World Prompt
        required:
        - world_prompt
        title: WorldsGenerateRequest
        type: object
      wlt__marble__v1__public_api__schemas__prompts__MultiImagePrompt:
        description: 'Multi-image-to-world generation.


          Generates a world from multiple images. text_prompt is optional.


          Recommended image formats: jpg, jpeg, png, webp.'
        properties:
          disable_recaption:
            anyOf:
            - type: boolean
            - type: 'null'
            description: If True, use text_prompt as-is without recaptioning
            title: Disable Recaption
          multi_image_prompt:
            description: List of images with optional spherical locations
            items:
              $ref: '#/components/schemas/wlt__marble__v1__public_api__schemas__prompts__SphericallyLocatedContent'
            title: Multi Image Prompt
            type: array
          reconstruct_images:
            default: false
            description: Whether to use reconstruction mode (allows up to 8 images,
              otherwise 4)
            title: Reconstruct Images
            type: boolean
          text_prompt:
            anyOf:
            - type: string
            - type: 'null'
            description: Optional text guidance (auto-generated if not provided)
            title: Text Prompt
          type:
            const: multi-image
            default: multi-image
            title: Type
            type: string
        required:
        - multi_image_prompt
        title: MultiImagePrompt
        type: object
      wlt__marble__v1__public_api__schemas__prompts__SphericallyLocatedContent:
        description: Content with a preferred location on the sphere.
        properties:
          azimuth:
            anyOf:
            - type: number
            - type: 'null'
            description: Azimuth angle in degrees
            title: Azimuth
          content:
            description: The content at this location
            discriminator:
              mapping:
                data_base64: '#/components/schemas/DataBase64Reference'
                media_asset: '#/components/schemas/MediaAssetReference'
                uri: '#/components/schemas/UriReference'
              propertyName: source
            oneOf:
            - $ref: '#/components/schemas/MediaAssetReference'
            - $ref: '#/components/schemas/UriReference'
            - $ref: '#/components/schemas/DataBase64Reference'
            title: Content
        required:
        - content
        title: SphericallyLocatedContent
        type: object
      wlt__marble__v1__public_api__schemas__prompts__VideoPrompt:
        description: 'Video-to-world generation.


          Generates a world from a video. text_prompt is optional.


          Recommended video formats: mp4, webm, mov, avi.

          Maximum video size: 100MB.'
        properties:
          disable_recaption:
            anyOf:
            - type: boolean
            - type: 'null'
            description: If True, use text_prompt as-is without recaptioning
            title: Disable Recaption
          text_prompt:
            anyOf:
            - type: string
            - type: 'null'
            description: Optional text guidance (auto-generated if not provided)
            title: Text Prompt
          type:
            const: video
            default: video
            title: Type
            type: string
          video_prompt:
            description: Video content for world generation
            discriminator:
              mapping:
                data_base64: '#/components/schemas/DataBase64Reference'
                media_asset: '#/components/schemas/MediaAssetReference'
                uri: '#/components/schemas/UriReference'
              propertyName: source
            oneOf:
            - $ref: '#/components/schemas/MediaAssetReference'
            - $ref: '#/components/schemas/UriReference'
            - $ref: '#/components/schemas/DataBase64Reference'
            title: Video Prompt
        required:
        - video_prompt
        title: VideoPrompt
        type: object
      wlt__marble__v1__public_api__schemas__prompts__WorldTextPrompt:
        description: 'Text-to-world generation.


          Generates a world from a text description. text_prompt is REQUIRED.'
        properties:
          disable_recaption:
            anyOf:
            - type: boolean
            - type: 'null'
            description: If True, use text_prompt as-is without recaptioning
            title: Disable Recaption
          text_prompt:
            anyOf:
            - type: string
            - type: 'null'
            description: Optional text guidance (auto-generated if not provided)
            title: Text Prompt
          type:
            const: text
            default: text
            title: Type
            type: string
        title: WorldTextPrompt
        type: object
      wlt__marble__v1__schema__api_schema__MultiImagePrompt:
        description: For world models supporting multi-image (+ text) input.
        properties:
          multi_image_prompt:
            items:
              $ref: '#/components/schemas/wlt__marble__v1__schema__api_schema__SphericallyLocatedContent'
            title: Multi Image Prompt
            type: array
          reconstruct_images:
            default: false
            title: Reconstruct Images
            type: boolean
          text_prompt:
            anyOf:
            - type: string
            - type: 'null'
            title: Text Prompt
          type:
            const: multi-image
            default: multi-image
            title: Type
            type: string
        required:
        - multi_image_prompt
        title: MultiImagePrompt
        type: object
      wlt__marble__v1__schema__api_schema__SphericallyLocatedContent:
        description: Content with a preferred location on the sphere.
        properties:
          azimuth:
            anyOf:
            - type: number
            - type: 'null'
            title: Azimuth
          data_base64:
            anyOf:
            - type: string
            - type: 'null'
            title: Data Base64
          extension:
            anyOf:
            - type: string
            - type: 'null'
            description: File extension without dot
            examples:
            - jpg
            - png
            - pdf
            - txt
            title: Extension
          uri:
            anyOf:
            - type: string
            - type: 'null'
            title: Uri
        title: SphericallyLocatedContent
        type: object
      wlt__marble__v1__schema__api_schema__VideoPrompt:
        description: For world models supporting video (+ text) input.
        properties:
          text_prompt:
            anyOf:
            - type: string
            - type: 'null'
            title: Text Prompt
          type:
            const: video
            default: video
            title: Type
            type: string
          video_prompt:
            $ref: '#/components/schemas/Content'
        required:
        - video_prompt
        title: VideoPrompt
        type: object
      wlt__marble__v1__schema__api_schema__WorldTextPrompt:
        description: Input prompt class for text-conditioned world generation.
        properties:
          text_prompt:
            anyOf:
            - type: string
            - type: 'null'
            title: Text Prompt
          type:
            const: text
            default: text
            title: Type
            type: string
        title: WorldTextPrompt
        type: object
    securitySchemes:
      ApiKeyAuth:
        description: API key for authentication. Get your key from the developer portal.
        in: header
        name: WLT-Api-Key
        type: apiKey
  info:
    description: Public-facing API for the Marble platform
    summary: Marble Public API v1
    title: Marble Public API v1
    version: 1.0.0
  openapi: 3.1.0
  paths:
    /marble/v1/:
      get:
        description: Health check endpoint.
        operationId: health_check_marble_v1__get
        responses:
          '200':
            content:
              application/json:
                schema:
                  title: Response Health Check Marble V1  Get
                  type: object
            description: Successful Response
        summary: Health Check
    /marble/v1/media-assets/{media_asset_id}:
      get:
        description: "Get a media asset by ID.\n\nRetrieves metadata for a previously\
          \ created media asset.\n\nArgs:\n    media_asset_id: The media asset identifier.\n\
          \nReturns:\n    MediaAsset object with media_asset_id, file_name, extension,\
          \ kind,\n    metadata, created_at, and updated_at.\n\nRaises:\n    HTTPException:\
          \ 404 if not found"
        operationId: get_media_asset_marble_v1_media_assets__media_asset_id__get
        parameters:
        - in: path
          name: media_asset_id
          required: true
          schema:
            title: Media Asset Id
            type: string
        responses:
          '200':
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/MediaAsset'
            description: Successful Response
          '422':
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/HTTPValidationError'
            description: Validation Error
        summary: Get Media Asset
    /marble/v1/media-assets:prepare_upload:
      post:
        description: "Prepare a media asset upload for use in world generation.\n\n\
          This API endpoint creates a media asset record and returns a signed upload\
          \ URL.\nUse this workflow to upload images or videos that you want to reference\
          \ in world\ngeneration requests.\n\n## Workflow\n\n1. **Prepare Upload** (this\
          \ endpoint): Get a `media_asset_id` and `upload_url`\n2. **Upload File**:\
          \ Use the signed URL to upload your file\n3. **Generate World**: Reference\
          \ the `media_asset_id` in `/worlds:generate` with\n   source type \"media_asset\"\
          \n\n## Request Parameters\n\n- `file_name`: Your file's name (e.g., \"landscape.jpg\"\
          )\n- `extension`: File extension without dot (e.g., \"jpg\", \"png\", \"mp4\"\
          )\n- `kind`: Either \"image\" or \"video\"\n- `metadata`: Optional custom\
          \ metadata object\n\n## Response\n\nReturns a `MediaAssetPrepareUploadResponse`\
          \ containing:\n\n- `media_asset`: Object with `media_asset_id` (use this in\
          \ world generation)\n- `upload_info`: Object with `upload_url`, `required_headers`,\
          \ and `curl_example`\n\n## Uploading Your File\n\nUse the returned `upload_url`\
          \ and `required_headers` to upload your file:\n\n```bash\ncurl --request PUT\
          \ \\\n  --url <upload_url> \\\n  --header \"Content-Type: <content-type>\"\
          \ \\\n  --header \"<header-name>: <header-value>\" \\\n  --upload-file /path/to/your/file\n\
          ```\n\nReplace:\n- `<upload_url>`: The `upload_url` from the response\n- `<content-type>`:\
          \ MIME type (e.g., `image/png`, `image/jpeg`, `video/mp4`)\n- `<header-name>:\
          \ <header-value>`: Each header from `required_headers`\n- `/path/to/your/file`:\
          \ Path to your local file\n\n## Example Usage in World Generation\n\nAfter\
          \ uploading, use the `media_asset_id` in a world generation request:\n\n```json\n\
          {\n  \"world_prompt\": {\n    \"type\": \"image\",\n    \"image_prompt\":\
          \ {\n      \"source\": \"media_asset\",\n      \"media_asset_id\": \"<your-media-asset-id>\"\
          \n    }\n  }\n}\n```"
        operationId: prepare_media_asset_upload_marble_v1_media_assets_prepare_upload_post
        requestBody:
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MediaAssetPrepareUploadRequest'
          required: true
        responses:
          '200':
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/MediaAssetPrepareUploadResponse'
            description: Successful Response
          '422':
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/HTTPValidationError'
            description: Validation Error
        summary: Prepare a media asset upload
    /marble/v1/operations/{operation_id}:
      get:
        description: "Get an operation by ID.\n\nPoll this endpoint to check the status\
          \ of a long-running operation.\nWhen done=true, the response field contains\
          \ the generated world.\n\nArgs:\n    operation_id: The operation identifier\
          \ from /worlds:generate.\n\nReturns:\n    GetOperationResponse[World] with:\n\
          \        - operation_id: Operation identifier\n        - created_at: Creation\
          \ timestamp\n        - updated_at: Last update timestamp\n        - expires_at:\
          \ Expiration timestamp\n        - done: true when complete, false while in\
          \ progress\n        - error: Error details if failed, null otherwise\n   \
          \     - metadata: Progress information and world_id\n        - response: Generated\
          \ World if done=true, null otherwise\n\nRaises:\n    HTTPException: 401 if\
          \ unauthorized\n    HTTPException: 404 if operation not found\n    HTTPException:\
          \ 500 if request fails"
        operationId: get_operation_marble_v1_operations__operation_id__get
        parameters:
        - in: path
          name: operation_id
          required: true
          schema:
            title: Operation Id
            type: string
        responses:
          '200':
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/GetOperationResponse_World_'
            description: Successful Response
          '422':
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/HTTPValidationError'
            description: Validation Error
        summary: Get Operation
    /marble/v1/worlds/{world_id}:
      get:
        description: "Get a world by ID.\n\nRetrieves a world's details including generated\
          \ assets if available.\nOnly the world owner or users with access to public\
          \ worlds can retrieve them.\n\nArgs:\n    world_id: The unique identifier\
          \ of the world.\n\nReturns:\n    World object with world_id, display_name,\
          \ tags, assets, created_at,\n    updated_at, permission, model, world_prompt,\
          \ and world_marble_url.\n\nRaises:\n    HTTPException: 404 if world not found\
          \ or access denied"
        operationId: get_world_marble_v1_worlds__world_id__get
        parameters:
        - in: path
          name: world_id
          required: true
          schema:
            title: World Id
            type: string
        responses:
          '200':
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/World'
            description: Successful Response
          '422':
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/HTTPValidationError'
            description: Validation Error
        summary: Get World
    /marble/v1/worlds:generate:
      post:
        description: "Start world generation.\n\nCreates a new world generation job\
          \ and returns a long-running operation.\nPoll the /operations/{operation_id}\
          \ endpoint to check generation status\nand retrieve the generated world when\
          \ complete.\n\nArgs:\n    request: The world generation request containing\
          \ world_prompt, display_name,\n        tags, model, seed, and permission settings.\n\
          \nReturns:\n    GenerateWorldResponse with operation_id and timestamps. Use\
          \ the operation_id\n    to poll for completion.\n\nRaises:\n    HTTPException:\
          \ 400 if invalid request or content violates policies\n    HTTPException:\
          \ 402 if insufficient credits\n    HTTPException: 500 if generation could\
          \ not be started"
        operationId: generate_world_marble_v1_worlds_generate_post
        requestBody:
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/WorldsGenerateRequest'
          required: true
        responses:
          '200':
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/GenerateWorldResponse'
            description: Successful Response
          '422':
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/HTTPValidationError'
            description: Validation Error
        summary: Generate World
    /marble/v1/worlds:list:
      post:
        description: "List worlds with optional filters.\n\nReturns worlds created through\
          \ the API with optional filtering and pagination.\n\nArgs:\n    request: List\
          \ request with optional filters:\n        - page_size: Number of results per\
          \ page (default: 10)\n        - page_token: Pagination token from previous\
          \ response\n        - status: Filter by status (e.g., \"COMPLETED\")\n   \
          \     - model: Filter by model name (e.g., \"Marble 0.1-plus\")\n        -\
          \ tags: Filter by tags (matches worlds with any tag)\n        - is_public:\
          \ Filter by visibility (true=public, false=private, null=all)\n        - created_after:\
          \ Filter by creation time (after timestamp)\n        - created_before: Filter\
          \ by creation time (before timestamp)\n        - sort_by: Sort order (\"created_at\"\
          \ or \"updated_at\")\n\nReturns:\n    ListWorldsResponse with worlds list\
          \ and next_page_token for pagination.\n\nRaises:\n    HTTPException: 400 if\
          \ invalid parameters\n    HTTPException: 500 if request fails"
        operationId: list_worlds_marble_v1_worlds_list_post
        requestBody:
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ListWorldsRequest'
          required: true
        responses:
          '200':
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/ListWorldsResponse'
            description: Successful Response
          '422':
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/HTTPValidationError'
            description: Validation Error
        summary: List Worlds
  security:
  - ApiKeyAuth: []
  servers:
  - description: World API
    url: https://api.worldlabs.ai
  ````
</Accordion>


# Get an Operation
Source: https://docs.worldlabs.ai/api/reference/operations/get

GET /marble/v1/operations/{operation_id}
Get an operation by ID.

Poll this endpoint to check the status of a long-running operation.
When done=true, the response field contains the generated world.

Args:
    operation_id: The operation identifier from /worlds:generate.

Returns:
    GetOperationResponse[World] with:
        - operation_id: Operation identifier
        - created_at: Creation timestamp
        - updated_at: Last update timestamp
        - expires_at: Expiration timestamp
        - done: true when complete, false while in progress
        - error: Error details if failed, null otherwise
        - metadata: Progress information and world_id
        - response: Generated World if done=true, null otherwise

Raises:
    HTTPException: 401 if unauthorized
    HTTPException: 404 if operation not found
    HTTPException: 500 if request fails



# Generate a World
Source: https://docs.worldlabs.ai/api/reference/worlds/generate

POST /marble/v1/worlds:generate
Start world generation.

Creates a new world generation job and returns a long-running operation.
Poll the /operations/{operation_id} endpoint to check generation status
and retrieve the generated world when complete.

Args:
    request: The world generation request containing world_prompt, display_name,
        tags, model, seed, and permission settings.

Returns:
    GenerateWorldResponse with operation_id and timestamps. Use the operation_id
    to poll for completion.

Raises:
    HTTPException: 400 if invalid request or content violates policies
    HTTPException: 402 if insufficient credits
    HTTPException: 500 if generation could not be started



# Get a World
Source: https://docs.worldlabs.ai/api/reference/worlds/get

GET /marble/v1/worlds/{world_id}
Get a world by ID.

Retrieves a world's details including generated assets if available.
Only the world owner or users with access to public worlds can retrieve them.

Args:
    world_id: The unique identifier of the world.

Returns:
    World object with world_id, display_name, tags, assets, created_at,
    updated_at, permission, model, world_prompt, and world_marble_url.

Raises:
    HTTPException: 404 if world not found or access denied



# List Worlds
Source: https://docs.worldlabs.ai/api/reference/worlds/list

POST /marble/v1/worlds:list
List worlds with optional filters.

Returns worlds created through the API with optional filtering and pagination.

Args:
    request: List request with optional filters:
        - page_size: Number of results per page (default: 10)
        - page_token: Pagination token from previous response
        - status: Filter by status (e.g., "COMPLETED")
        - model: Filter by model name (e.g., "Marble 0.1-plus")
        - tags: Filter by tags (matches worlds with any tag)
        - is_public: Filter by visibility (true=public, false=private, null=all)
        - created_after: Filter by creation time (after timestamp)
        - created_before: Filter by creation time (before timestamp)
        - sort_by: Sort order ("created_at" or "updated_at")

Returns:
    ListWorldsResponse with worlds list and next_page_token for pagination.

Raises:
    HTTPException: 400 if invalid parameters
    HTTPException: 500 if request fails



# Welcome to Marble
Source: https://docs.worldlabs.ai/index

Marble helps you create high-fidelity, persistent 3D worlds.

<iframe title="Welcome to Marble" />

Marble is the first product from World Labs and is powered by our multimodal world models that can reconstruct, generate, and simulate 3D worlds. Marble lets anyone create high-fidelity, persistent 3D worlds from a single text prompt, single or multiple image, video, and coarse 3D structures.

This guide provides an overview of the Marble interface and the library of guides, tutorials, and templates for creating a world. Our goal is to help you jumpstart the world creation process so that you can publish and share your worlds with the world.

## Navigating Marble

Marble's interface is organized into several main sections to streamline your world creation workflow:

* <Icon icon="compass" /> **Gallery** - Browse and explore worlds created by the community, discover inspiration, and access your own created worlds
* <Icon icon="brush" /> **Create** - The main workspace for generating new 3D worlds using various input methods like text, images, videos, or 3D structures
* <Icon icon="palette" /> **Studio** - Advanced tools for editing, composing multiple worlds together, and creating cinematic recordings of your environments

## Creating a World

Marble offers multiple ways to create 3D worlds, each tailored to different creative workflows and input types:

### <Icon icon="panels-top-left" /> Preset

Browse and select curated preset examples to quickly generate worlds based on popular themes and styles, or <Icon icon="dices" /> roll for marbles to select a random one.

### <Icon icon="type" /> Text Prompt

Create worlds from natural language descriptions. Simply describe your vision and let Marble's AI generate a complete 3D environment.

### <Icon icon="image" /> Single Image

Transform any photograph or artwork into an immersive 3D world. Perfect for bringing 2D concepts into explorable 3D spaces. [Explore image prompt techniques →](/marble/create/prompt-guides/image-prompt)

### <Icon icon="images" /> Multiple Images

Combine multiple images to specify more visual details in the world. You can specify directional positioning of each image (Front, Back, Left, Right) or use Auto Layout [Discover multi-image creation →](/marble/create/prompt-guides/multi-image-prompt)

### <Icon icon="equal-approximately" />Panorama

Upload 360° panoramic images for maximum control over world layout and the most accurate spatial representation. [Learn panoramic world creation →](/marble/create/prompt-guides/pano-prompt)

### <Icon icon="video" /> Video

Upload short video clips (under 100MB) to provide rich spatial information. Ideal for capturing 360° rotational views of spaces. [Master video-based world creation →](/marble/create/prompt-guides/video-prompt)

### <Icon icon="box" /> 3D Structure ("Chisel")

Use Marble's built-in 3D modeling tools to block out geometric layouts and architectural structures as the foundation for detailed world generation. [Get started with Chisel →](/marble/create/chisel-tools/chisel-basics)

### <Icon icon="repeat" /> Reuse Prompt

Quickly iterate on existing worlds by reusing successful prompts and modifying them for new variations.

## Editing a World

Enhance and modify your created worlds using Marble's powerful editing capabilities:

### <Icon icon="move" /> Pano Edit

Edit your worlds through their panoramic representation. Select specific areas and describe changes using natural language prompts to make targeted modifications while preserving the overall environment. [Learn pano editing techniques →](/marble/edit/pano-edit)

### <Icon icon="expand" /> Click and Expand

Grow your worlds beyond their original boundaries by clicking on unexplored areas and generating seamless extensions that naturally connect to existing content. [Master world expansion →](/marble/edit/click-and-expand)

### <Icon icon="shuffle" /> Variation

Generate alternative versions of your worlds while maintaining core elements and style, perfect for exploring different possibilities from the same starting point. [Explore variation techniques →](/marble/edit/variation)

## Studio Tools

Take your world creation to the next level with advanced studio capabilities:

### <Icon icon="layers" /> Compose

Connect and arrange multiple existing worlds into larger, seamless environments. Perfect for creating game maps, architectural complexes, or expansive connected experiences. [Learn world composition →](/marble/create/studio-tools/compose)

### <Icon icon="video" /> Record

Create cinematic camera animations and record smooth flythrough videos of your worlds. Ideal for showcasing environments, creating trailers, or producing professional presentations. [Master animation recording →](/marble/create/studio-tools/record)

## Exporting a World

Share and use your created worlds across different platforms and applications:

### <Icon icon="download" /> Download Options

Access various export formats depending on your intended use:

* **Web Sharing** - Copy shareable links for browser-based viewing and exploration
* **VR Experience** - Generate VR-compatible links for immersive virtual reality viewing
* **Development Assets** - Export 3D models and textures for use in game engines and development tools
* **DCC Integration** - Download files compatible with digital content creation software like Blender, Maya, and 3ds Max
* **Mesh Export** - Export clean 3D geometry for 3D printing, CAD software, or further modeling work

[Explore all export options →](/marble/export)

## Platform Compatibility

Marble is available on the web for both desktop and mobile. Some features are not yet supported on mobile (e.g., advanced creation flow with editing tools, creating from 3D structures, pano viewing), so we recommend using Marble on desktop for the full experience.

## Generation Times

We're constantly working to make it faster to generate worlds in Marble. Current estimated generation times:

* **Create pano from text, image, or 3D structure**: \~30 sec
* **Create pano from multi-image or video**: \~2 min
* **Create draft (from any input)**: \~20 sec
* **Create world (from any input)**: \~5 min
* **Expand world**: \~5 min
* **Edit pano**: \~20 sec
* **Generate high-quality mesh**: \~1 hr

## Getting Help

### <Icon icon="info" /> Frequently Asked Questions

Find answers to common questions about credits, file formats, sharing, VR access, and more. [Browse the FAQ →](/marble/support/faq)

### <Icon icon="credit-card" /> Billing and Support

Learn about account management, billing information, and how to get additional support. [Visit billing and support →](/marble/support/account-billing)

Ready to start creating? Head to the [Create](/marble/create/prompt-guides) section to begin your first world, or explore the [Gallery](https://marble.worldlabs.ai) to see what's possible with Marble.


# Chisel basics
Source: https://docs.worldlabs.ai/marble/create/chisel-tools/chisel-basics

Create detailed 3D worlds from coarse 3D blocking.

<iframe title="Welcome to Marble" />

# Chisel Scene: 3D World Blocking

Use the Chisel Scene to quickly block out 3D spaces and create the foundation for detailed worlds. This tool lets you build geometric layouts that serve as the base structure for your generated environments.

## Getting Started with Chisel Scene

Enter Chisel from the omnibox, select <Icon icon="cube" /> 3D Input mode, and enter Chisel by <Icon icon="pickaxe" /> Start.

The Chisel Scene interface provides essential tools for 3D world creation:

* **3D Viewport**: The main canvas where you build your world geometry
* **Geometry Panel**: Access tools like Walls and Panorama Camera
* **Template Options**: Upload GLB or FBX models to start from existing geometry
* **Generation Controls**: Text prompt input and Generate button

## How to Block Out Walls for a Room

To create a basic room structure:

1. **Start with the Wall Tool**: In the Geometry panel, select **Walls**
2. **Draw Wall Boundaries**: Click and drag in the 3D Viewport to define wall perimeters
3. **Close the Room**: Connect your final wall segment back to the starting point
4. **Adjust Height**: Use the wall handles to modify wall height as needed
5. **Add Doorways**: Create openings by selecting wall segments and adjusting them

## How to Set Up Camera Views

Position your viewpoint for world generation:

1. **Select Panorama Camera**: Click on **Panorama Camera** in the Geometry panel
2. **Position the Camera**: Place it where you want the generated view to originate
3. **Adjust Height**: Drag the camera vertically to set the viewing height
4. **Orient the View**: Rotate the camera to face the desired direction

## How to Upload Reference Geometry

Start with existing 3D models:

1. **Click Upload**: Select **Upload a glb or fbx model** in the template section
2. **Choose Your File**: Browse and select your 3D model file
3. **Position the Model**: The uploaded geometry appears in the viewport
4. **Scale if Needed**: Adjust the model size using the transformation handles

## How to Generate Your World

Transform your blocked-out geometry into a detailed environment:

1. **Add a Text Prompt**: In the text input, describe your desired environment (e.g., "modern kitchen")
2. **Click Generate**: Press the **Generate** button to create your world
3. **Wait for Processing**: The system will generate detailed geometry based on your blocks and prompt

## FAQ

### What is the Chisel Tool?

The <Icon icon="pickaxe" />**Chisel** tool lets you modify and refine existing geometry by carving, extruding, or reshaping elements.

### What does the Extrude Tool do?

The **Extrude Tool** (Z key) extends selected surfaces outward or inward, allowing you to create depth and volume from flat shapes.

### What is the Wall Tool used for?

The **Wall Tool** (X key) specifically creates vertical wall segments, perfect for defining room boundaries and architectural elements.

### How do I delete geometry?

Use the **Delete** tool (<Icon icon="delete" />) to remove selected elements from your scene. You can also press the **Delete** key after selecting objects.

### What does the Undo function do?

**Undo** (⌘Z) reverses your last action, letting you step back through your modeling history if you make mistakes.

### When should I use Public Mode?

Enable **Public Mode** when you want your created world to be visible to other users in the community gallery. Leave it disabled for private projects.

### What file formats can I upload?

The template uploader supports **GLB** and **FBX** file formats for 3D models. These are common formats exported from most 3D modeling software.


# Overview
Source: https://docs.worldlabs.ai/marble/create/index

Ways to generate new worlds with prompts, images, video, and Chisel

Pick the best way to begin imagining your world:

<Card title="Prompt guides" href="/marble/create/prompt-guides">
  Learn how to create your first world by prompting Marble with text, images, or video.
</Card>

<Card title="Chisel tools" href="/marble/create/chisel-tools">
  Use Marble's built-in 3D modeling tools to block out geometric layouts and architectural structures as the foundation for detailed world generation.
</Card>

<Card title="Studio tools" href="/marble/create/studio-tools">
  Take your world creation to the next level with advanced studio capabilities: compose and arrange multiple existing worlds into larger, seamless environments, or create cinematic camera animations and record smooth flythrough videos of your worlds.
</Card>


# Advanced create
Source: https://docs.worldlabs.ai/marble/create/prompt-guides/advanced-create

Multi-stage advanced workflow for pixel perfect world creation

<iframe title="Advanced Create" />

The Advanced Create workflow in Marble gives you precise control over your world generation through a multi-stage process. Instead of jumping directly to a final world, you can refine and edit at each stage to ensure the perfect result.

## Multi-Stage Creation Process

Start by dragging in your prompt into the omnibox under the <Icon icon="image" /> 2D input mode. Check the "use advanced editing" box, and click on <Icon icon="brush" /> Create to jump into the advanced workflow.

The advanced workflow breaks world creation into distinct stages, each offering opportunities for refinement:

### Stage 1: Pano

* **Purpose**: Establish the initial panoramic representation of your world
* **Input**: Your original prompt (text, image, video, etc.)
* **Output**: A 360° panoramic view that captures the spatial layout and visual elements

### Stage 2: Panorama Edit (Optional)

* **Purpose**: Refine specific areas of the panorama before world generation
* **Process**:
  * Directly describe changes in the prompt box, and <Icon icon="banana" /> Apply edit for global changes, or
  * Select edit area in the panoramic view and describe desired changes in the prompt box and <Icon icon="banana" /> Apply edit for targeted local changes, or
  * <Icon icon="image-plus" /> Add images to add image references for the edit, and describe desired changes in the prompt box and <Icon icon="banana" /> Apply edit for adding ingredients into the panorama.
* **Use Cases**:
  * Adjust lighting or colors
  * Modify objects
  * Add or remove details
  * Fix any issues with the initial panoramic generation
* **Tips**:
  * You can <Icon icon="drafting-compass" /> Queue Draft creation in the background by clicking on each panorama thumbnail. You will get a notification when it finishes, and you can find the results in your "Worlds" tab from the side-nav.

<iframe title="Panorama Edit Tutorial" />

### Stage 3: Draft

* **Purpose**: Generate a quick 3D preview to evaluate spatial structure
* **Output**: A lightweight 3D world for rapid assessment
* **Benefits**: Preview the 3D structure and identify any needed changes before full processing. If any details stand out, you can further edit the panorama to change it.

### Stage 4: World Generation

* **Purpose**: Create the final high-quality 3D world
* **Process**: Full processing of the panorama into a complete 3D environment
* **Output**: Complete navigable 3D world ready for exploration and export
* **Tips**:
  * Toggle "Public mode" to change if generated world will be visible from public gallery.

## Additional Tips

* Jump back into the advanced editing flow with <Icon icon="brush" /> Continue creating.

## When to Use Advanced Create

The Advanced Create workflow is ideal when you need:

* **Precision Control**: Fine-tune specific elements before committing to full world generation
* **Professional Projects**: Commercial work requiring precise results and iterative feedback
* **Learning and Experimentation**: Understanding how changes at different stages affect the final output

The Advanced Create workflow transforms world generation from a single-step process into a refined, iterative experience that puts creative control in your hands.


# Expand
Source: https://docs.worldlabs.ai/marble/create/prompt-guides/expand

Expand: Improving low fidelity regions of your world.

<iframe title="Expand" />

Use Expand to extend your existing worlds beyond their current boundaries.
This tool lets you seamlessly grow your environments by clicking on unexplored areas and
generating new content that naturally connects to your existing world.

## How to Access Expand

For any generated world, hit the <Icon icon="paintbrush" /> **Continue Creating** paintbrush icon within the viewer or within your worlds tab to access the Expand tool.

## Getting Started with Expand

1. **Navigate Your World**: Move around using standard controls to explore your current boundaries
2. **Look for Edges**: Find areas where your world meets unexplored space
3. **Check for Warnings**: The system shows "Not within recommended area" when you're near expansion zones
4. **Position Yourself**: Move to a good viewpoint of the area you want to expand
5. **Click Expand**: Press the **Expand** button in the bottom panel

## How to Plan Strategic Expansions

## Advanced Expansion Techniques

### Strategic Positioning

* **Doorway Extensions**: Expand beyond doorways to create connected rooms
* **Corner Expansions**: Expand from corners to see large new areas
* **Landscape Extensions**: Extend outdoor areas to create larger environments

## Common Expansion Scenarios

### Indoor Extensions

* Expand bedrooms into en-suite bathrooms
* Extend kitchens into dining areas or pantries
* Add hallways connecting separate rooms
* Create balconies or terraces from indoor spaces

### Outdoor Growth

* Expand gardens into larger landscaped areas
* Extend courtyards into street views or neighboring buildings
* Add pathways leading to new outdoor zones
* Create transitions from indoor to outdoor spaces

### Architectural Additions

* Add wings to buildings or structures
* Extend rooflines or architectural features
* Create connecting bridges or walkways
* Add levels or floors to existing structures

## FAQ

### What does "Not within recommended area" mean?

This warning appears when you're either too close to existing content or beyond the limits for expansion. It helps you identify where new content can be generated.

### How do I know where I can expand?

Look for areas where your world meets unexplored or blurry spaces. These boundary zones are where expansion is possible.

### Will new areas match my existing world's style?

Yes, the expansion system analyzes your existing world's visual style, architecture,
and aesthetic to generate new areas that naturally fit and connect with your current environment.

### Can I expand in multiple directions?

Currently, you can perform one expansion of your world in different directions. You can
export the results to studio for stitching.

### What happens if I don't like an expansion?

Each expansion creates a new version while preserving previous states. You can return
to earlier versions or try expanding in different directions from your original world.

### How do expansions connect to existing areas?

The system automatically creates seamless transitions between your existing world and
new areas, ensuring proper lighting, scale, and architectural continuity at the
connection points.

### Can I expand upwards or downwards?

Not at the moment.


# Image prompt tips
Source: https://docs.worldlabs.ai/marble/create/prompt-guides/image-prompt

How to create sharp scenes with image prompt

# Creating Worlds from Images

Transform your photos and images into immersive 3D worlds with Marble's image-to-world generation. Learn how to select the best images and optimize your prompts for stunning results.

## Getting Started with Image Prompts

Image prompting in Marble works by analyzing your uploaded image and generating a 3D environment based on its content, style, and composition. The AI understands spatial relationships, lighting, and architectural elements to create explorable worlds. You can do so dragging in images to the omnibox; it will expand with <Icon icon="image" /> 2D input mode, which allows you to start a generation by clicking on <Icon icon="brush" /> Create. For image file specifications, see [Prompt Guidelines →](/guides/prompt_guidelines)

## Choosing the Right Images

### Image Quality Guidelines

**Resolution and Clarity**

* Use high-resolution images (minimum 1024x1024 pixels)
* Ensure good lighting and clear details
* Avoid heavily compressed or pixelated images
* Sharp focus is preferred over blurry images

  <Note>
    Images need to be under 20Mb
  </Note>

**Composition Tips**

* Images with clear depth and perspective work best
* Multiple spatial elements create richer worlds
* Good balance between foreground, midground, and background
* Avoid flat or purely decorative images

## Optimizing Your Image Selection

### What Works Well

* **Clear Spatial Definition**: Images where you can see floors, walls, ceilings, or ground planes
* **Multiple Elements**: Scenes with furniture, objects, or architectural details
* **Good Lighting**: Natural or artificial lighting that defines the space

### What to Avoid

* **Close-up Shots**: Extreme close-ups of objects without spatial context
* **Characters**: Human and animals are not well supported by the model yet.
* **Blurry Images**: Blurry images result in ambiguous 3D interpretations.
* **Abstract Images**: Pure abstractions without recognizable spatial elements
* **Flat Graphics**: Logos, text, or 2D graphics without depth
* **Poor Lighting**: Very dark, overexposed, or unclear images
* **Images with Border**: Crop your image carefully to avoid flat patches of image border showing up in the 3D world.

Remember that Marble's AI interprets your image creatively, so the generated world may expand beyond what's visible in your original image, creating a fuller, explorable environment.


# Prompt guidelines
Source: https://docs.worldlabs.ai/marble/create/prompt-guides/index

Input requirements and specifications for Marble world generation

## Text prompts

* Up to 2,000 characters
* Describe a location, such as "A warm, rustic cabin living room with a glowing stone fireplace, cozy leather sofa, wooden beams, and large windows overlooking a snowy forest."

## Images

* Recommended resolution: 1024 on the long side
* Recommended aspect ratio: 16:9, 9:16, or anything in between
* Max file size: 20 MB
* Supported formats: png (recommended), jpg, webp
* See [Image Prompt Guide](./image-prompt) and [Multi-image Prompt Guide](./multi-image-prompt).

## Panoramas

* full 360 degree equirectangular projection, in 2:1 aspect ratio.
* Recommended resolution: 2560 pixels wide
* See [Panorama Prompt Guide](./pano-prompt).

## Video

* Max file size: 100 MB
* Max duration: 30 seconds
* Supported formats: mp4, mov, webm
* See [Video Prompt Guide](./video-prompt).

## 3D structure uploads ("Chisel" Import)

* Max file size: 100 MB
* Supported formats: glb, fbx


# Multi-image prompt tips
Source: https://docs.worldlabs.ai/marble/create/prompt-guides/multi-image-prompt

Specify more details by combining multiple images.

<iframe title="Multi-image Prompt Tips" />

# Creating Worlds with Multiple Images with Direction Control

In the <Icon icon="image" /> 2D input mode of omnibox, drag in or upload up to 4 images.
Click on the text overlay on image thumbnails to change its direction, and choose one from "Front", "Back", "Left", "Right".
For this mode, images without overlap allow the marble models to creatively fill in the spaces between views.
When you are done specifying the direction of each image, click on <Icon icon="brush" /> Create to generate the world.
For image file specifications, see [Prompt Guidelines →](/marble/create/prompt-guides)

* Direction Control is great for connecting different environments creatively.

# Creating Worlds with Multiple Images with Auto Layout

In the <Icon icon="image" /> 2D input mode of omnibox, drag in or upload up to 8 images.
Toggle "Auto Layout" switch to on so the world model automatically determines the relative positioning of these images.
In this mode, all uploaded images need to share the same aspect ratio and resolution, and should be images from the same space.
Currently images captured in close proximity of each other but covering different viewing directions, and with some overlap between images, work the best.
Click on <Icon icon="brush" /> Create to generate the world.

* Auto Layout is great for quick reconstruction of existing spaces.

## Troubleshooting Multi-Image Issues

### "Auto Layout not working properly"

* **Verify Aspect Ratios**: Ensure all images have exactly the same width-to-height ratio
* **Check for Overlap**: Include visual elements that appear in multiple images
* **Improve Image Quality**: Use sharp, well-lit images with clear details
* **Check Lighting Consistency**: Try to match lighting conditions and color temperatures
* **Use Images from Same Location**: Confirm all images are truly of the same space

Multi-image prompting allows you to build more complex, interesting worlds than single images alone.
The key is thoughtful planning of how your images relate spatially and visually to create cohesive, explorable environments.


# Pano prompt tips
Source: https://docs.worldlabs.ai/marble/create/prompt-guides/pano-prompt

Use panoramas for maximum control over the world.

# Creating Worlds from Panoramic Images

Upload 360° panoramic images to create immersive 3D worlds with maximum control over your environment.
Panoramas provide complete spatial information, allowing for more accurate and detailed world generation than standard images.

## Getting Started with Panorama Upload

You can obtain a full 360 equirectangular panorama by capturing it with a 360 camera,
rendering it from a 3D software, or downloading from a Marble world.
To create a world with panorama, you can simply drag and drop it to the omnibox; it
will expand with <Icon icon="image" /> 2D input mode.
Check the left and right edge of your panorama is continuous for best results.
If the image is successfully recognized as a panorama, a <Icon icon="panorama" />
icon will appear on the image thumbnail. You can then start a
generation by clicking on <Icon icon="brush" /> Create.

## Troubleshooting Common Issues

### "Image is not recognized as a panorama"

* **Check Aspect Ratio**: Ensure exactly 2:1 width to height ratio
* **Check sky and ground coverage**: Phone panoramas often lack full vertical 180 coverage

### "Seam visible in generated world"

* **Fix Source Panorama**: Repair edge alignment in image editing software,
* **"Use advanced editing"**: to edit panorama with AI assistance on Marble.

## Frequently Asked Questions

### Are multi panorama inputs supported?

* **Not directly**: Multiple panoramic images cannot be uploaded together in a single generation. However, you can create larger worlds by generating a world from each panorama separately, then stitching them together using [Studio Compose](/marble/create/studio-tools/compose).

Panoramic uploads give you the most control over the final world layout, as the 360° image provides complete spatial information for the AI to work with.


# Video prompt tips
Source: https://docs.worldlabs.ai/marble/create/prompt-guides/video-prompt

How to create a world with a video

# Creating Worlds from Video

Upload short videos to create immersive 3D worlds with rich spatial information.
Videos provide multiple perspectives of your space, allowing the AI to understand depth
and spatial relationships better than a single images alone.

## Getting Started with Video Upload

Drag a short video of a static space into the omnibox; it will expand with <Icon icon="image" /> 2D input mode,
which allows you to start a generation by clicking on <Icon icon="brush" /> Create.
For video file specifications, see [Prompt Guidelines →](/marble/create/prompt-guides)

## Best Practices for Video Capture

### Camera Movement Guidelines

* **Rotation Focus**: Rotate the camera to cover a large viewing angle
* **Avoid motion blur**: Use steady, controlled camera movements to avoid excessive motion blur
* **Wide Coverage**: Aim to capture 180° to 360° of the space
* **Continuous Shot**: Record one uninterrupted take of the space

### Camera Settings

* **Fixed Focal Length**: Avoid zooming in or out during recording
* **Fixed Exposure**: Avoid changing exposure during recording

Video provides the richer spatial information for world generation, as the AI can analyze multiple perspectives and understand how different elements relate in 3D space.


# Compose
Source: https://docs.worldlabs.ai/marble/create/studio-tools/compose

Connect and arrange multiple worlds to create larger, seamless environments for games and experiences.

<iframe title="Welcome to Marble" />

# Studio Compose: Building Connected Worlds

Use Studio Compose to connect multiple existing worlds into larger, seamless environments. Perfect for creating game maps, architectural complexes, or any scenario where you need to join separate scenes into one cohesive experience.

## Getting Started with Compose

The Studio Compose interface provides powerful tools for world arrangement:

* **3D Viewport**: The main canvas showing your connected worlds
* **Scene Panel**: Manage and add worlds to your composition
* **Controls Panel**: Fine-tune positioning, rotation, and scaling
* **Project Tools**: Save, share, and export your composed world

## How to Add Worlds to Your Composition

Build your composition by importing existing worlds:

1. **Click Add Scene**: In the Scene panel, select **Add** to browse your worlds
2. **Choose Your World**: Select from your saved worlds or community creations
3. **Position the World**: The world appears in the viewport with positioning handles
4. **Repeat as Needed**: Add multiple worlds to build your larger environment

## Splat Removal

2. **Brush:** Use circle or square brushes to delete splats.
3. **Brush Size:** Adjust the brush size for more precise control.

## How to Position and Align Worlds

Precisely control world placement:

1. **Select a World**: Click on any world in the viewport or Scene panel
2. **Use Position Controls**: In the Controls panel, adjust X, Y, Z coordinates
3. **Set Rotation**: Modify rotation values to orient worlds correctly
4. **Adjust Scale**: Change the scale value to resize worlds proportionally
5. **Visual Alignment**: Use the grid and bounding corners for visual reference

## How to Navigate Your Composition

Move around your large-scale environment:

1. **Adjust Move Speed**: Set movement speed (default: 3) for comfortable navigation
2. **Enable Natural Mouse**: Toggle natural mouse controls for intuitive camera movement
3. **Set Field of View (FOV)**: Adjust to 92 or your preferred viewing angle
4. **Use Grid Reference**: Toggle grid visibility to help with alignment
5. **Show Bounding Corners**: Enable to see world boundaries clearly

## How to Fine-Tune World Connections

Create seamless transitions between worlds:

1. **Check Overlapping Areas**: Look for where worlds meet or overlap
2. **Align Ground Levels**: Ensure floor heights match between connected worlds
3. **Match Lighting**: Adjust worlds so lighting conditions blend naturally
4. **Test Transitions**: Navigate between worlds to check for smooth movement
5. **Adjust Background Color**: Set consistent background (BG Color: #3f3f3f) across scenes

## How to Save and Export Your Composition

Preserve and share your connected world:

1. **Save Your Project**: Use the save controls to preserve your composition
2. **Share Settings**: Enable sharing if you want others to view your creation
3. **Export Options**: Use the Export button to generate files for external use
4. **Monitor Splats**: Keep track of your splat usage (500,000 / 2,000,000 limit shown)

## FAQ

### What does the splat count represent?

Splats represent the 3D Gaussian Splat data that makes up your worlds. The counter shows your current usage against your account limit. Larger, more detailed worlds use more splats.

### What is the Layer panel for?

The Layer panel lets you organize and manage the visibility of different worlds in your composition. You can hide or show specific worlds while working.

### How do I delete a world from my composition?

Select the world you want to remove and press delete key. The world will be removed from the composition but remains in your library.


# Record
Source: https://docs.worldlabs.ai/marble/create/studio-tools/record

Create cinematic camera animations and record smooth flythrough videos of your worlds.

<iframe title="Welcome to Marble" />

# Record: Creating Camera Animations

Use Record to create smooth camera animations and capture cinematic flythroughs
of your worlds. Perfect for showcasing environments, creating trailers, or producing
professional presentations of your 3D scenes.

<Warning>
  **Important: Data Persistence Limitation**

  Currently the trajectory does not persist. You **WILL lose the keyframes** when you leave the page. Similarly, you **WILL lose the enhanced video** if you leave the page. Stay on the page until your (enhanced) videos have finished downloading.
</Warning>

## Getting Started with Record

The Studio Record interface provides comprehensive animation tools:

* **3D Viewport**: View your world with camera animation preview
* **Camera Frustum**: Yellow wireframe showing camera view and movement path
* **Animation Timeline**: Control playback, timing, and keyframes
* **Playback Controls**: Play, pause, and scrub through your animation
* **Export Tools**: Enhance and export your final video

## How to Set Up Your Camera Animation

Create smooth camera movements through your world:

1. **Position Your Camera**: Move to your desired starting viewpoint in the 3D viewport
2. **Set First Keyframe**: The camera frustum (yellow wireframe) shows your view cone
3. **Move to Next Position**: Navigate to where you want the camera to move
4. **Add More Keyframes**: Build your camera path with multiple positions
5. **Preview Movement**: The yellow path lines show your camera's trajectory

## How to Control Animation Timing

Fine-tune the pacing of your camera movement:

1. **Use the Timeline**: The bottom timeline shows seconds
2. **Scrub Through Time**: Drag the blue playhead to preview different moments
3. **Adjust Keyframe Timing**: Move keyframes along the timeline to change pacing
4. **Set Animation Length**: Extend or shorten the total duration as needed
5. **Preview Timing**: Use playback controls to test your animation speed

## How to Preview Your Animation

Review your camera movement before recording:

1. **Click Play**: Use the <Icon icon="play" /> play button to start animation preview
2. **Pause and Adjust**: Use <Icon icon="pause" /> pause to stop and make adjustments
3. **Scrub Timeline**: Drag the playhead to jump to specific moments
4. **Check Camera Path**: Watch the yellow frustum move along the path
5. **View from Animation**: The preview window shows your camera's perspective

## How to Record and Export

Capture your final animation:

1. **Preview First**: Ensure your animation looks correct using the preview controls
2. **Use Enhance**: Click <Icon icon="sparkles" /> **Enhance** to improve video quality and effects. Wait on this page until the enhance is done.
3. **Download Video**: Click <Icon icon="download" /> **Download** to download your final animation file

## FAQ

### What does the yellow wireframe represent?

The **Camera Frustum** (yellow wireframe cone) shows exactly what your camera sees at each moment, including the field of view and viewing direction. The lines connecting different positions show your camera's movement path.

### How long can my animation be?

The timeline extends beyond 8 seconds, allowing for longer animations. However, longer videos may take more time to process and export.

### What does the Enhance feature do?

**Enhance** applies post-processing effects like improved lighting, color grading, and visual effects to make your video look more professional and cinematic.

### Can I edit keyframes after creating them?

Yes, you can move keyframes along the timeline to adjust timing, and reposition your camera at any keyframe to change the path.

### What file formats can I export?

A mp4 video.

### How do I create smooth camera movements?

Focus on gentle curves rather than sharp angles, use consistent speeds between keyframes, and preview frequently to ensure the movement feels natural.

## Keyboard Shortcuts and Controls Reference

Master the Studio Record interface with these keyboard shortcuts and button tooltips for efficient animation workflow.

### Animation Keyframe Controls

Create and manage keyframes with these essential shortcuts:

* **F** - <Icon icon="diamond-plus" /> Add keyframe at current camera position
* **U** - <Icon icon="switch-camera" /> Update selected keyframe to current camera position
* **Delete/Backspace** - <Icon icon="diamond-minus" /> Delete selected keyframe

### Timeline Playback Controls

Navigate through your animation timeline efficiently:

* **Space** - <Icon icon="play" />/<Icon icon="pause" /> Toggle play/pause animation
* **G** - <Icon icon="skip-back" /> Jump to beginning of timeline
* **H** - <Icon icon="step-back" /> Jump to previous keyframe
* **L** - <Icon icon="step-forward" /> Jump to next keyframe
* **;** (semicolon) - <Icon icon="skip-forward" /> Jump to end of timeline

### Seek and Scrubbing Controls

Fine-tune your position in the animation:

* **J** - <Icon icon="rewind" /> Seek backward (hold to continue seeking)
* **K** - <Icon icon="fast-forward" /> Seek forward (hold to continue seeking)

### Camera Movement Controls

Navigate your 3D world while setting up animations:

* **W** - Move Forward
* **A** - Move Left
* **S** - Move Backward
* **D** - Move Right
* **E** - Move Up
* **Q** - Move Down
* **Shift** - Speed Up movement

### View Controls

Adjust your viewing perspective:

* **\[** - Decrease Field of View (FOV)
* **]** - Increase Field of View (FOV)
* **0** - Return to Origin position

### Timeline Interface Buttons

The timeline interface includes these interactive controls with tooltips:

#### Playback Controls Section

* <Icon icon="skip-back" /> "Jump to beginning (G)" - Moves playhead to start of timeline
* <Icon icon="step-back" /> "Jump to previous keyframe (H)" - Moves playhead to previous keyframe
* <Icon icon="play" />/<Icon icon="pause" /> "Play" / "Pause (Space)" - Toggles animation playback
* <Icon icon="step-forward" /> "Jump to next keyframe (L)" - Moves playhead to next keyframe
* <Icon icon="skip-forward" /> "Jump to end (;)" - Moves playhead to end of timeline

### Pro Tips for Efficient Animation Workflow

1. **Add keyframes frequently** - Add keyframes with F as you explore to build smooth camera paths
2. **Preview with Space** - Constantly test your animation timing with the play shortcut
3. **Scrub with H/L** - Fine-tune timing by holding these keys to seek through your animation
4. **Speed up navigation** - Hold Shift while moving to quickly position your camera
5. **Reset with 0** - Return to origin if you get lost while positioning your camera


# Exporting to Blender
Source: https://docs.worldlabs.ai/marble/export/gaussian-splat/blender

Import Marble worlds into Blender using Gaussian Splatting plugins

<video />

There are a couple of Blender plugins available, and we've looked into the following.

<AccordionGroup>
  <Accordion title="KIRI Engine">
    The [**KIRI Engine**](https://www.kiriengine.app/blender-addon/3dgs-render) plugin for Blender is the most well-known and actively maintained option! We've verified it works on Blender 4.2+.
  </Accordion>

  <Accordion title="Reshot AI">
    Some users reported a better experience working with the [**Reshot AI**](https://github.com/ReshotAI/gaussian-splatting-blender-addon) plugin, preferring it over the more maintained KIRI engine plugin, and stating that it was more performant and flexible.
  </Accordion>

  <Accordion title="SplatForge">
    The [SplatForge](https://splatforge.cloud) plugin is the most performant/responsive Blender option we've seen so far! However, the render pass is entirely separate from Blender's main render loops (EEVEE/Cycles), so compositer graph workarounds are needed to combine splats with other Blender geometry.
  </Accordion>

  <Accordion title="Jetset iOS" icon="sparkles">
    The [Jetset iOS app](https://docs.lightcraft.pro/tutorials/blender-workflows/gaussian-splat-setup) allows you to first set up your splats in Blender via a modified Reshot AI plugin, then do virtual production on your phone! We've had a **ton** of fun with this one.
  </Accordion>
</AccordionGroup>

If you have had positive or negative experiences with any of these plugins, we appreciate your feedback and will be updating this page as we go.

<Accordion title="Community FAQ">
  ### Q: Why does the lighting look different in point cloud vs splat mode in ReshotAI? The lighting is darker in splat mode.

  **A:** This is unavoidable due to how splats are represented as differently sized geometry in point cloud vs splat mode. In splat mode, the per-splat meshes are denser, so they occlude the lighting in the scene more. Neither lighting mode is "correct" - they're just different representations.

  There are two solutions:

  1. **Place lights within the scene:** Treat the splats as solid geometry and position your lights strictly within the scene.
  2. **Make lights ignore splats for shadow-casting:** Click on the light → Object tab → Shading → Shadow Linking, then drag the splats into a new collection in that tab and uncheck it. This prevents the splats from casting shadows on other objects in your scene.
     <small>[discord discussion](https://discord.com/channels/1288765343552110637/1448516454055153674)</small>

  ***

  ### Q: How does ReshotAI compare to other Blender plugins?

  **A:** Based on user feedback, ReshotAI is the easiest and most straightforward option out of the plugins tested. While it may not look as great in point cloud mode (giving the Gaussian splats a more "dreamy" look), users have reported preferring it over other options like KIRI Engine and GS loader for its simplicity and ease of use. However, note that the GS loader method doesn't emit lights for objects in the scene, so it relies entirely on your scene lighting.
  <small>[discord discussion](https://discord.com/channels/1288765343552110637/1448516454055153674)</small>
</Accordion>


# Exporting to Houdini
Source: https://docs.worldlabs.ai/marble/export/gaussian-splat/houdini

Import Marble worlds into Houdini using Gaussian Splatting plugins

<video />

The <Icon icon="sparkles" /> [**GSOPs plugin**](https://github.com/cgnomads/GSOPs/tree/develop) is actively maintained and has a lot of great additional splat-related features around splat animation and splat conversions to vdb/mesh. We've verified it works on Houdini 20.5.

If you have had positive or negative experiences with this plugin, we appreciate your feedback and will be updating this page as we go.


# Exporting from Marble
Source: https://docs.worldlabs.ai/marble/export/gaussian-splat/index

Take your Marble content to popular 3D engines and platforms!

## Format

We currently support **gaussian splats exports** for all our content.

You can find the file specs and sample files for different options in the
[Export File Specs](/guides/export-options/options#splats).

<Tip>
  The lower-resolution files have been optimized to be as perceptually similar as possible to the higher-resolution files. For those of you working with applications where lighter compute is important, we encourage you to give this a try! You may convert these to .ply files [here](https://spz-to-ply.netlify.app) if needed.
</Tip>

## Integration

The [Radiance Fields](https://radiancefields.com/3d-gaussian-splatting-engine-support) website provides a comprehensive overview of platforms and plugins supporting splat integration. Here is a non-exhaustive subset of tools and platforms that we’ve either tested ourselves or received positive feedback from our user community about.

Click on one of these sub-categories to get started!

<Columns>
  <Card title="Spark" icon="sparkle" href="/guides/export-options/spark">
    *Build custom applications using the spark.js framework for three.js developers.*

    \
    Provides the highest degree of control and customization for web-based applications. Perfect for creating VR experiences, interactive games, and custom visualization tools.
  </Card>

  <Card title="Professional Software" icon="palette">
    *Great for professional studios or creators using well-known tools like Unreal Engine, Unity, Houdini, or Blender.*

    These integrate well with offline production pipelines in established 3D software ecosystems. They allow teams to fit Gaussian Splat workflows into existing VFX, animation, or game development pipelines without needing to build tooling from scratch.

    **[Unreal Engine](/guides/export-options/unreal)**,
    **[Unity](/guides/export-options/unity)**,
    **[Blender](/guides/export-options/blender)**,
    **[Houdini](/guides/export-options/houdini)**
  </Card>

  <Card title="Web Platforms (Coming Soon!)" icon="globe">
    *Great for artists or teams prioritizing one-stop solutions and fast iteration over deep customization.*

    \
    These focus on ease of sharing and distribution, often requiring minimal setup. Perfect for quickly showcasing work or creating interactive experiences that can be accessed directly in a browser.
  </Card>
</Columns>

We greatly appreciate the contributions and feedback from our user community on these so far— if you have insights or experiences with other export options, please share them with us on Discord and we will update these resources as we go!


# Exporting to Dev Frameworks
Source: https://docs.worldlabs.ai/marble/export/gaussian-splat/spark

Take Marble into your own custom apps!

For the three.js devs out there, check out [**spark**](https://sparkjs.dev/)! Some examples of what you can build on spark include [**lofi worlds**](https://lofiworlds.ai/marble) in VR, and a [**first person shooting game**](https://github.com/bmild/spark-physics) with animated characters.

<video />

We highly recommend this option. It is also what our own website is built off of, so you'll have the most native experience utilitizing this library. spark devs are also hanging out in our discord and are ready to answer your questions!


# Exporting to Unity
Source: https://docs.worldlabs.ai/marble/export/gaussian-splat/unity

Import Marble worlds into Unity using Gaussian Splatting plugins

<video />

The free [**aras-p plugin**](https://github.com/aras-p/UnityGaussianSplatting) works well on Unity 6.1! Users have also reported positive results with this plugin. However, note that users have also reported draw-order issues in bringing multiple splat components in. So if you want to use multiple marble worlds in the same level, you may need to combine them into a single component beforehand.

If you have had positive or negative experiences with this plugin, we appreciate your feedback and will be updating this page as we go.

<Accordion title="Community FAQ">
  ### Q: I'm getting an "Index out of range" error when trying to import 500k splats in Unity. The 2M splats work fine, but the low-res ones don't load.

  **A:** This is a known issue with the 500k spz files. As a workaround, convert the 500k spz file to a ply file using the converter at [https://spz-to-ply.netlify.app/](https://spz-to-ply.netlify.app/). The converted 500k ply file should import into Unity without issues. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1421913319538954472)</small>

  ***

  ### Q: How can I convert a splat into a working 3D mesh inside Unity so I can interact with it and try new things?

  **A:** There's nothing inside Unity that supports converting splats to meshes. The only plugin we're aware of that supports this is the Houdini GSOPs plugin. We have collider meshes and high quality mesh baking natively in Marble though! <small>[discord discussion](https://discord.com/channels/1288765343552110637/1421913319538954472)</small>

  ***

  ### Q: My splat renders fine in Unity's Game view, but when I export to Quest 3 VR, I get a completely black screen. What's wrong?

  **A:** Enable HDR on your URP asset. This simple setting fix resolves the black screen issue in VR builds. Make sure HDR is enabled in your Universal Render Pipeline asset settings. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1421913319538954472)</small>

  ***

  ### Q: What Unity version should I use for VR projects with splats?

  **A:** Use Unity 6.0 (specifically 6000.0.23f1 or similar). The aras-p plugin does not work for VR on Unity 6.3. After downgrading to 6.0, make sure you have all the XR packages installed and check your graphics API settings. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1421913319538954472)</small>

  ***

  ### Q: What are the recommended settings for getting splats working in VR on Quest 3?

  **A:** Here's the recommended setup:

  * **Unity Version:** 6.0 (6000.0.23f1 or similar)
  * **Plugin:** aras-p UnityGaussianSplatting package
  * **Render Pipeline:** URP (Universal Render Pipeline) with HDR enabled
  * **Graphics API:** Vulkan
  * **Rendering Mode:** Multi-view (not Single Pass Instanced - SPI causes black screens when the headset is active)
  * **XR Packages:** Make sure all XR packages are installed

  Both URP and BiRP (Built-in Render Pipeline) work, but URP is recommended. The visual quality looks the same between them. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1421913319538954472)</small>

  ***

  ### Q: I'm getting a "PLY vertex size mismatch, expected 252 but file has 68" error with the ninjamode Gaussian splat VR plugin. The same file works fine with the aras plugin.

  **A:** Unfortunately, we haven't tested the ninjamode plugin ourselves and can't advise on it. The aras-p plugin is the recommended solution for Unity splat imports. We've put the ninjamode plugin on our list to try out in the future. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1421913319538954472)</small>

  ***

  ### Q: I can't get Multi-pass rendering to work in VR - it automatically switches back to Single-pass when I open it in VR.

  **A:** This is expected behavior. Multi-view rendering works, but Single Pass Instanced (SPI) causes black screens when the headset is active. Stick with Multi-view rendering for VR builds. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1421913319538954472)</small>

  ***

  ### Q: What's the performance like with splats on Quest 3?

  **A:** Based on testing:

  * **2M splat files:** Cause Quest 3 builds to crash when opening. Not recommended for standalone VR.
  * **500k splat files:** Work better for VR, with better small details than 2M files in some cases. Performance is around 12fps in Unity, compared to 19fps in PlayCanvas (via Oculus browser). The 500k files are more suitable for standalone VR, while 2M files may only be viable for desktop VR. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1421913319538954472)</small>

  ***

  ### Q: I need to place assets inside my Marble environment, but they're falling through the floor even though I have a mesh collider component on the GLB. Any tips?

  **A:** This question was raised but not fully resolved in the discussion. The GLB mesh collider may need additional configuration. We're planning to support coarse nav meshes and collider meshes natively in Marble soon, which should help with physics interactions. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1421913319538954472)</small>

  ***

  ### Q: Which splat export format should I use for Unity?

  **A:** Marble offers three export options:

  * **2M ply** - Full resolution PLY format
  * **2M spz** - Full resolution SPZ format
  * **500K spz** - Lower resolution SPZ format

  For Unity, the 2M spz files work out of the box. The 500k spz files have a known issue and need to be converted to ply format using [https://spz-to-ply.netlify.app/](https://spz-to-ply.netlify.app/) before importing. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1421913319538954472)</small>

  ***

  ### Q: The aras plugin works in the sample project, but when I try to use it in an empty project, the .ply file doesn't show up at all.

  **A:** Make sure you have all the required XR packages installed and that your graphics API is set correctly (Vulkan for VR). Also ensure HDR is enabled on your URP asset. Try recreating the setup from the aras-p sample project to ensure all dependencies are properly configured. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1421913319538954472)</small>
</Accordion>


# Exporting to Unreal Engine
Source: https://docs.worldlabs.ai/marble/export/gaussian-splat/unreal

Import Marble worlds into Unreal Engine using Gaussian Splatting plugins

<video />

There are a couple Unreal plugins currently available for Windows.

<AccordionGroup>
  <Accordion title="Postshot (Recommended)" icon="sparkles">
    The [**Postshot**](https://www.jawset.com/docs/d/Postshot+User+Guide/Unreal+Engine+Integration) plugin for Unreal works reliably (we've verified it works on UE5.2)! A free version is available, but you need to upgrade for the full set of functionality and for commercial use.\
    \
    It currently can only be run on Windows machines that have the standalone Postshot software installed. You'll need to import .ply files into Postshot and save out in postshot format (.psht) before loading into Unreal.
  </Accordion>

  <Accordion title="Volinga (Recommended)" icon="sparkles">
    The paid [**Volinga**](https://web.volinga.ai/#VolingaPlugin) plugin has been a popular option amongst our virtual production users and comes with additional features specific to virtual production.
  </Accordion>

  <Accordion title="Akiya">
    The [**Akiya**](https://vrlab.akiya-souken.co.jp/en/products/threedgaussianplugin/) plugin works pretty well! We suggest considering this option as well, but it is slightly more costly than Postshot and Volinga.
  </Accordion>

  <Accordion title="Luma / XVerse">
    While the [XVerse](https://github.com/xverse-engine/XScene-UEPlugin) and [Luma](https://www.fab.com/listings/b52460e0-3ace-465e-a378-495a5531e318) plugins are completely free, they are not actively maintained and our users have had partial-but-limited success with these.

    In particular, XVerse is functional on UE5.2 but may come with some visual artefacts from under-the-hood aggressive optimizing / downsampling!
  </Accordion>
</AccordionGroup>

If you have had positive or negative experiences with any of these plugins, we appreciate your feedback and will be updating this page as we go.

<Accordion title="Community FAQ">
  ### Q: Which Unreal Engine plugin supports depth of field with splats and meshes together?

  **A:** For depth of field support, **Volinga** is potentially the best option, especially for virtual production use cases. The **3D Gaussians Plugin** (Akiya) also supports depth of field and works with nDisplay. Note that Postshot didn't work well with nDisplay according to user reports. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1422034485934821497)</small>

  ***

  ### Q: How can I get depth of field to work with splats in Unreal Engine?

  **A:** You can change the splat material from translucent to masked with AA Temporal Dither. This allows depth of field to work correctly, but note that it will slightly lower the visual quality compared to translucent materials. To do this, open the large Niagara node and look at the bottom section where you'll see the material your particles use. Change the material blend mode from translucent to masked and enable AA Temporal Dither. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1422034485934821497)</small>

  ***

  ### Q: Why do my splats look low resolution in Unreal compared to viewing them on the Marble site?

  **A:** The **XVerse** plugin does internal downsampling that causes artifacts and reduces splat density. This is a known issue with that plugin. **Postshot** doesn't have this low resolution issue. Also, make sure you're not downloading files as "SPZ Low-res" format, as that will naturally have fewer splats. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1422034485934821497)</small>

  ***

  ### Q: Does Postshot add a watermark to my Unreal Engine scenes?

  **A:** Yes, Postshot implements a watermark icon in the Unreal Engine scene when you import a .psht file. This watermark appears in the scene view. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1422034485934821497)</small>

  ***

  ### Q: Can I still use the Luma plugin for Unreal Engine?

  **A:** No, Luma no longer supports its Unreal Engine plugin and it won't work properly. The plugin was discontinued and is not actively maintained. Even in UE 5.3 (the last supported version), the plugin doesn't function correctly. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1422034485934821497)</small>

  ***

  ### Q: How can I convert SPZ files to PLY format for use with different plugins?

  **A:** You can use the online converter at [https://spz-to-ply.netlify.app/](https://spz-to-ply.netlify.app/) to convert SPZ files to PLY format. This is useful if you need to use a plugin that requires PLY format or if you're experiencing issues with SPZ files. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1422034485934821497)</small>

  ***

  ### Q: Which plugin works best for virtual production with nDisplay?

  **A:** **Volinga** is the recommended option for virtual production and nDisplay compatibility. Postshot had issues with nDisplay according to user reports. The **3D Gaussians Plugin** (Akiya) also supports nDisplay and depth of field, though it's more expensive. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1422034485934821497)</small>

  ***

  ### Q: I'm getting texture errors when importing PLY files with XV3DGS in Unreal Engine 5.5. Is this normal?

  **A:** Yes, this is a known issue. In UE 5.5, XV3DGS shows texture errors when importing PLY files. On first import, you may see an empty cube, and after reloading, you may see a gray mesh. This is expected behavior with this plugin in 5.5. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1422034485934821497)</small>

  ***

  ### Q: My material status shows "none" after importing with XV3DGS. Will anything work?

  **A:** If the material status is "none", the splats won't render properly. Try exporting your Marble world as SPZ format and converting it to PLY using [https://spz-to-ply.netlify.app/](https://spz-to-ply.netlify.app/) before importing. Make sure you haven't modified the particle material or textures in the import folder. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1422034485934821497)</small>

  ***

  ### Q: What's the best plugin for depth of field and nDisplay support if I'm willing to pay?

  **A:** The **3D Gaussians Plugin** (Akiya) is expensive but offers the most reliable solution. It supports depth of field, works with nDisplay, has an automatic splitting system to divide scenes into multiple Niagara effects for full quality, and provides better quality than XVerse. It's less problematic than other plugins according to user reports. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1422034485934821497)</small>

  ***

  ### Q: Can I change the material settings in XVerse/XScene-UEPlugin to enable depth of field?

  **A:** While it's theoretically possible to change the material from translucent to masked in the Niagara component, users have reported that Unreal Engine crashes when attempting this with the XScene-UEPlugin. The material settings may be locked or cause instability with this particular plugin. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1422034485934821497)</small>

  ***

  ### Q: Does Postshot still allow exporting to PLY format in the free version?

  **A:** No, the Postshot plugin no longer allows exporting as PLY if you don't have a paid subscription. This is a limitation of the free version. <small>[discord discussion](https://discord.com/channels/1288765343552110637/1422034485934821497)</small>
</Accordion>


# Mesh export
Source: https://docs.worldlabs.ai/marble/export/mesh



<iframe title="Mesh Export" />

# Mesh Export: Downloading 3D Assets

Export your Marble worlds as 3D meshes for use in game engines, 3D software, and other
applications. Choose from multiple mesh formats and quality levels to suit your specific
needs, from quick prototyping to high-quality production assets.

## Getting Started with Collider Mesh Export

You can export collider mesh along with a splat to provide simple physics for games.
For example, see [**first person shooting game**](https://github.com/bmild/spark-physics).
To download collider mesh, navigate to the <Icon icon="download" /> download menu from
world viewer, or world in <Icon icon="globe" /> Worlds, and download from the
<Icon icon="triangle" /> Collider Mesh (GLB) link.

## Getting Started with High Quality Mesh Export

1. **Trigger Offline Generation**: Select
   <Icon icon="rectangle-ellipsis" /> **High-quality mesh (GLB)** from your world's
   export options
2. **Wait for Processing**: <Icon icon="loader-2" /> High-quality mesh generation takes up to an hour to complete
3. **Continue Working**: You can close tabs and browser windows - the process continues in the background
4. **Download When Ready**: Return later to find a
   <Icon icon="pyramid" /> **High-quality mesh (GLB)** button replacing the generate option
5. **Access Premium Quality**: Download detailed meshes, one around 600k triangles and
   texture maps, another around 1M triangles with vertex colors.

## FAQ

### How long does offline mesh generation take?

High-quality mesh generation could take up to 1 hour, depending on world complexity and
system load. You can close your browser and the process will continue in the background.

### Can I use collider meshes for visual rendering?

No. **Collider meshes** are optimized for physics interactions and have simplified geometry.
For visual rendering, use splats or the high-quality offline-generated meshes instead.

### How do I know when my offline mesh is ready?

Return to your world's <Icon icon="download" /> download menu after several hours.
The <Icon icon="rectangle-ellipsis" /> **High-quality mesh (GLB)** or option will be
replaced with a <Icon icon="pyramid" /> **High-quality mesh (GLB)** button when processing
is complete.

### What's included with high-quality meshes?

High-quality meshes include detailed geometry (around 600k triangles), and texture maps
. Some versions also include vertex color data for additional
material flexibility. See examples on [Export File Specs →](/marble/export/specs).

### Can I cancel offline mesh generation?

Currently, once started, offline mesh generation runs to completion in the background.

### What's the file size of exported meshes?

File sizes vary by complexity and format. Collider mesh are typically 3-4 MB,
while high-quality meshes with textures are typical around 100 - 200 MB depending on
world details. See examples on [Export File Specs →](/marble/export/specs).


# Export file specs
Source: https://docs.worldlabs.ai/marble/export/specs

Tech specs on export files

### Images

* <Icon icon="image-plus" /> **Prompt image**:
  * prompt from which the world is generated
* <Icon icon="scan" /> **360 Panorama**:
  * Equirectangular png of 2560 x 1280 pixels

### Splats

* <Icon icon="triangle-dashed" /> **Splats (SPZ)**:
  * Splat-based format optimized for Marble's rendering system, about 2M splats
* <Icon icon="triangle-dashed" /> **Splats (low-res SPZ)**:
  * Splat-based format optimized for Marble's rendering system, about 500k splats
* <Icon icon="triangle-dashed" /> **Splats (PLY)**:
  * Splat file with broader software compatibility, about 2M splats
* <Icon icon="triangle-dashed" /> **Splats (low-res PLY)**:
  * Splat file with broader software compatibility, about 500k splats

### Mesh

* <Icon icon="triangle" /> **Collider Mesh (GLB)**
  * coarse mesh optimized for simple physics calculations
  * glb format
  * 100-200k triangles
* <Icon icon="pyramid" /> **High-quality mesh (GLB)**
  * One glb around 600k triangles, with texture information
  * Another glb around 1M triangles, with vertex colors
  * Takes up to an hour to generate
  * Currently rate limited to 4 generation requests per hour per user
  * You can only generate high quality mesh on worlds you own

## Example files

Here we provide a few example scenes and export files to test against.

### Gaussian Splats

Scroll to the right to see all options.

| Scene                                                                                                        | SPZ 2m                                                                                                                                          | SPZ 500k                                                                                                                                          | PLY 2m                                                                                                                                          | PLY 500k                                                                                                                                          |
| ------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Rustic kitchen with natural light](https://marble.worldlabs.ai/world/69a9fc22-63ad-4e4c-9514-065b9aa56340)  | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/rustic_kitchen_with_natural_light/rustic_kitchen_with_natural_light_2m.spz)   | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/rustic_kitchen_with_natural_light/rustic_kitchen_with_natural_light_500k.spz)   | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/rustic_kitchen_with_natural_light/rustic_kitchen_with_natural_light_2m.ply)   | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/rustic_kitchen_with_natural_light/rustic_kitchen_with_natural_light_500k.ply)   |
| [Elegant library with fireplace](https://marble.worldlabs.ai/world/20fc27f9-5b1f-4c76-8b22-67b866195aaf)     | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/elegant_library_with_fireplace/elegant_library_with_fireplace_2m.spz)         | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/elegant_library_with_fireplace/elegant_library_with_fireplace_500k.spz)         | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/elegant_library_with_fireplace/elegant_library_with_fireplace_2m.ply)         | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/elegant_library_with_fireplace/elegant_library_with_fireplace_500k.ply)         |
| [Modern house with lush landscaping](https://marble.worldlabs.ai/world/e1d2610d-32a7-4364-acbb-8fcc97c1933d) | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/modern_house_with_lush_landscaping/modern_house_with_lush_landscaping_2m.spz) | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/modern_house_with_lush_landscaping/modern_house_with_lush_landscaping_500k.spz) | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/modern_house_with_lush_landscaping/modern_house_with_lush_landscaping_2m.ply) | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/modern_house_with_lush_landscaping/modern_house_with_lush_landscaping_500k.ply) |
| [Narrow European cobblestone lane](https://marble.worldlabs.ai/world/54fad6e4-9c9b-43ba-be6d-f1e31cbe7a95)   | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/narrow_european_cobblestone_lane/narrow_european_cobblestone_lane_2m.spz)     | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/narrow_european_cobblestone_lane/narrow_european_cobblestone_lane_500k.spz)     | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/narrow_european_cobblestone_lane/narrow_european_cobblestone_lane_2m.ply)     | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/narrow_european_cobblestone_lane/narrow_european_cobblestone_lane_500k.ply)     |
| [Warm traditional kitchen interior](https://marble.worldlabs.ai/world/30ac948d-6b19-4191-a12e-4ce4510ccfe7)  | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/warm_traditional_kitchen_interior/warm_traditional_kitchen_interior_2m.spz)   | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/warm_traditional_kitchen_interior/warm_traditional_kitchen_interior_500k.spz)   | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/warm_traditional_kitchen_interior/warm_traditional_kitchen_interior_2m.ply)   | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/warm_traditional_kitchen_interior/warm_traditional_kitchen_interior_500k.ply)   |

### Image & Mesh

| Scene                                                                                                        | 360 Pano                                                                                                                                          | Collider mesh GLB                                                                                                                                     | HQ mesh GLB                                                                                                                                     |
| ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [Rustic kitchen with natural light](https://marble.worldlabs.ai/world/69a9fc22-63ad-4e4c-9514-065b9aa56340)  | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/rustic_kitchen_with_natural_light/rustic_kitchen_with_natural_light_pano.png)   | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/rustic_kitchen_with_natural_light/rustic_kitchen_with_natural_light_collider.glb)   | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/rustic_kitchen_with_natural_light/rustic_kitchen_with_natural_light_hq.glb)   |
| [Elegant library with fireplace](https://marble.worldlabs.ai/world/20fc27f9-5b1f-4c76-8b22-67b866195aaf)     | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/elegant_library_with_fireplace/elegant_library_with_fireplace_pano.png)         | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/elegant_library_with_fireplace/elegant_library_with_fireplace_collider.glb)         | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/elegant_library_with_fireplace/elegant_library_with_fireplace_hq.glb)         |
| [Modern house with lush landscaping](https://marble.worldlabs.ai/world/e1d2610d-32a7-4364-acbb-8fcc97c1933d) | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/modern_house_with_lush_landscaping/modern_house_with_lush_landscaping_pano.png) | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/modern_house_with_lush_landscaping/modern_house_with_lush_landscaping_collider.glb) | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/modern_house_with_lush_landscaping/modern_house_with_lush_landscaping_hq.glb) |
| [Narrow European cobblestone lane](https://marble.worldlabs.ai/world/54fad6e4-9c9b-43ba-be6d-f1e31cbe7a95)   | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/narrow_european_cobblestone_lane/narrow_european_cobblestone_lane_pano.png)     | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/narrow_european_cobblestone_lane/narrow_european_cobblestone_lane_collider.glb)     | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/narrow_european_cobblestone_lane/narrow_european_cobblestone_lane_hq.glb)     |
| [Warm traditional kitchen interior](https://marble.worldlabs.ai/world/30ac948d-6b19-4191-a12e-4ce4510ccfe7)  | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/warm_traditional_kitchen_interior/warm_traditional_kitchen_interior_pano.png)   | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/warm_traditional_kitchen_interior/warm_traditional_kitchen_interior_collider.glb)   | [<Icon icon="download" />](https://wlt-ai-cdn.art/example_exports/warm_traditional_kitchen_interior/warm_traditional_kitchen_interior_hq.glb)   |

## FAQ

### What's the difference between SPZ and PLY formats?

SPZ is Marble's native splat format optimized for file size, while PLY is a
uncompressed format compatible with more Gaussian splat software packages.

### Why are my splats / meshes up-side-down when I export them to other software?

Default world labs worlds are in OpenCV coordinate system (+x left, +y down, +z forward).
Many DCC software are in the OpenGL coordinate system (+x left, -y down, -z forward).
To correct for it, perform an OpenCV-to-OpenGL transformation by scaling the Y and Z
axes by -1 (keeping X unchanged).
[See more on coordinate systems.](https://stackoverflow.com/questions/44375149/opencv-to-opengl-coordinate-system-transform)


# Release notes
Source: https://docs.worldlabs.ai/marble/release-notes

Latest updates and improvements to Marble

## December 11, 2025

### Features and Improvements

* Record mode in Studio now gives you more creative control: You can now freely move the floating preview window as you plan your flythrough, and you now have **expanded video export settings for quality**, resolution, aspect ratio, frame rate and codec (compression format) to tailor your final video.
* Improved export compatibility with external tools: World generations now export in the OpenGL coordinate system (previously OpenCV) for both splats and meshes. SPZ splats in Studio now export by default in SPZ v2 format (v3 still available as opt-in).

### Bug Fixes

* Fixed bugs around world generation status and added better error messaging for failed generations.
* Fixed bug around display of thumbnails for in-progress world generations.
* Fixed a bug in Compose mode within Studio where importing the same world twice caused edits to be shared across both imported worlds.
* Fixed bugs around payment downgrade/cancellation processing.

## December 5, 2025

### Features and Improvements

* Added ability to take screenshots of 360° panoramas.
* Added option to remove previously linked payment methods from your account.
* Upgraded pano editing to the latest high-quality model version. As part of this update, the credit cost per pano edit has been adjusted from **50 to 150 credits**.

### Bug Fixes

* Fixed issue that prevented some projects from loading in Marble Studio.
* Fixed transform handles not being clickable in **Compose** mode.
* Fixed bug causing **video export in Animate** mode to fail on certain devices.
* Fixed issue where **Chisel panorama view** restricted camera controls after returning to the page.
* Fixed several bugs around **payment success**, **downgrades**, and **cancellation** flows.

## November 20, 2025

### Features and Improvements

* Marble Studio now supports editing and composing significantly larger worlds using a new **Level-of-Detail splat-rendering backend**. Performance should remain stable as you scale up to more worlds and higher splat counts.
* **World IDs** are now displayed in the Worlds section, making it easier to share them with support for debugging.

### Bug Fixes

* Fixed bug where some world generations appeared to be ongoing/spinning for long durations of time without finishing.
* Fixed bug where users could exceed their available credit balances and were subsequently charged for the overage amount when upgrading their subscription plans. Also corrected a credit-to-dollar conversion issue that could overstate the overage amount. Refunds have been issued and all balances were restored to their original subscription credit amounts.
* Fixed bug that caused some users to be unable to upgrade their subscriptions.


# Subscriptions & billing
Source: https://docs.worldlabs.ai/marble/support/account-billing

Manage your Marble subscription, credits, and billing settings.

# Subscriptions & Billing

## How does Marble's pricing work?

Marble uses a credit-based subscription system, with higher tiers unlocking more features and credits. This guide explains how the plans, credits, and feature unlocks work so you can choose the right plan for your needs.

Credits are used each time you take an action in Marble.

Our current pricing can be found [here](https://marble.worldlabs.ai/pricing).

## What are the different subscription options?

Marble offers four subscription tiers, each with a monthly credit allocation and access to different capabilities.

### Free plan

Good for exploring the basics of what Marble can do

* Lightweight intro to Marble that lets you generate worlds from a text prompt, single image, or 360 panorama
* Includes up to 4 world generations

### Standard plan

Best for hobbyist users creating and editing worlds

* Adds creation tools for richer world building, including:
  * Generation from multiple images, videos, or 3D layouts
  * Editing your worlds
  * Exporting your worlds
  * Downloading worlds from the Marble community
* Includes up to 12 world generations

### Pro plan

Ideal for professional creators, artists, designers and engineers

* Unlocks advanced workflows, including:
  * Expanding worlds to larger spaces
  * Enhancing the quality of generated video outputs
  * Exporting high-quality textured meshes
  * Includes commercial rights to generated worlds
* Includes up to 25 world generations

### Max plan

Designed for users creating at scale

* Enables high-volume production
* Includes up to 75 world generations

## Do you offer an enterprise plan?

Yes, we offer custom plans for large teams and organizations that need flexible solutions at scale. [Contact us here](https://marble.worldlabs.ai/enterprise) to talk to our sales team.

## How do credits work?

Credits are used each time you take an action in Marble. The number of credits used depends on the complexity of the action (see current pricing [here](https://marble.worldlabs.ai/pricing)).

For example, a basic world generation from a single image uses a combination of 1,500 "world generation" credits + 80 "input method" credits, for a total of 1,580 credits.

An advanced world generation from multiple images that is then edited twice and expanded once uses a combination of 100 "input" credits + 1,500 "world generation + (2 × 150) "edit pano" credits + 2,000 "expand world" credits, for a total of 3,900 credits.

## Do unused credits roll over? How do I purchase additional credits?

Unused credits that come with your subscription plan (for example, the 20,000 credits that come with a Standard plan) do not roll over to the next month of your account billing cycle.

All paid plans allow you to purchase additional top-up credits at any time when you run out. Unlike credits that come with your subscription plan, top-up credits roll over to the next month. Top-up credits expire 1 year from the date of purchase.

When you take an action in Marble, your subscription credits will be used first before any top-up credits you've purchased are used.

## Will my plan automatically renew?

Yes, your plan will automatically renew at the end of your billing cycle.

## How do I upgrade my plan?

You can upgrade your plan by navigating to your Account page on the lower left of Marble, clicking "Manage account," clicking "Manage subscription," and selecting the plan you'd like to upgrade to.

Your upgrade will be effective immediately and you'll have access to the new tier's features right away.

You'll receive a prorated refund for any unused credits from your old plan, calculated using the per credit cost of your old plan. This refund will automatically be applied to the total cost of your new plan, and you will be invoiced for the remaining balance.

For example, if you upgrade from Standard to Pro tier and currently have 5,000 credits remaining in your Standard plan, you'll receive a refund of 5,000 × (\$20/month for Standard plan ÷ 20,000 credits in Standard plan) = \$5. Your upgrade cost will then become \$35/month for Pro plan, less the \$5 credit, for a net cost of \$30.

Any top-up credits you have in your account won't be affected and will roll over into your new plan.

## How do I downgrade my plan?

You can downgrade your plan by navigating to your Account page on the lower left corner of Marble, clicking "Manage account," clicking "Manage subscription," and selecting the plan you'd like to downgrade to. You'll retain access to all the features of your old plan until the end of your billing period, at which point you'll be downgraded to the new plan. Note that no pro-rated refund will be provided.

Any top-up credits you have in your account won't be affected and will roll over into your new plan.

## How do I cancel my plan?

You can cancel your plan by navigating to your Account page on the lower left corner of Marble, clicking "Manage account," clicking "Manage subscription," and clicking the "Cancel subscription" button beneath your current plan. You'll retain access to all the features of your current plan until the end of your billing period, at which point you'll return to the Free plan. Note that no pro-rated refund will be provided.

If you wish to close your account, please reach out to [support@worldlabs.ai](mailto:support@worldlabs.ai).


# FAQ
Source: https://docs.worldlabs.ai/marble/support/faq

Common questions and answers about Marble!

### How can I insert characters?

Currently, this can be done by exporting to Spark or other software. Learn more here: [https://t.co/r4Dia8P7c8](https://t.co/r4Dia8P7c8)

### Is there an API available?

Yes! See [platform.worldlabs.ai](platform.worldlabs.ai) for more information.

### How do I share my world with others?

Click on your world card to open the preview, then use the "Copy link" button to share a web link that others can view in their browser.

### How do I experience the world in VR?

Open your world card and use the "Copy VR link" button to get a VR-compatible link, or click the VR icon to open the world directly in your VR headset.

### Where can I read more about World Labs policies?

Please view our [Terms of Service](/terms-of-service) and [Privacy Policy](/privacy-policy) for details.


# Support & feedback
Source: https://docs.worldlabs.ai/marble/support/support-feedback

Join our community, get support, and share feedback to help shape the future of Marble.

## Join our community

In addition to the learning resources found here, you can also join the World Labs
[Discord](https://discord.gg/jSSSgXWT3v) server to connect with other creators and get
more information. We announce product updates, listen to your feature requests, and
even host live events. It's where our creators from around the world come together to
brainstorm ideas and showcase the latest projects they're working on in Marble.

Want more? Check out our [YouTube](https://www.youtube.com/@WorldLabsAI) channel and
follow us on [X](https://x.com/theworldlabs) and
[Instagram](https://www.instagram.com/theworldlabs/?igsh=NTc4MTIwNjQ2YQ%3D%3D#) to stay
up to date.

## Get support & share feedback

Have questions or feedback? Head over to the 🤝│ help channel in
[Discord](https://discord.gg/jSSSgXWT3v) to get support and the 💡 | ideas-and-features
channel to report a bug or share your feature ideas. We welcome all feedback to help us
shape the future of Marble!

We look forward to seeing the worlds you create!

## Review World Labs policies

Looking for more details? View our [Terms of Service](/terms-of-service) and [Privacy Policy](/privacy-policy).

