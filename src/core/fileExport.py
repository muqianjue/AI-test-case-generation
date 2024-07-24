import os
class fileExport:
    def file_export(self, base64, path, type1):
        content = f"""
                        <style>
                            .download-button {{
                                display: inline-flex;
                                -webkit-box-align: center;
                                align-items: center;
                                -webkit-box-pack: center;
                                justify-content: center;
                                font-weight: 400;
                                font-size: 1rem
                                padding: 0px;
                                border-radius: 0.5rem;
                                min-height: 2.5rem;
                                margin: -5px;
                                line-height: 1.6;
                                color: inherit;
                                width: auto;
                                user-select: none;
                                background-color: rgb(255, 255, 255);
                                border: 1px solid rgba(49, 51, 63, 0.2);

                        }}
                        .download-button:hover {{
                            background-color: #45a049;
                        }}
                        </style>

                            <div data-testid="column" class="st-emotion-cache-keje6w e1f1d6gn3" style="display: flex; justify-content: center; align-items: center; height: 100%;">
                              <div data-testid="stVerticalBlockBorderWrapper" data-test-scroll-behavior="normal" class="st-emotion-cache-0 e1f1d6gn0">
                                <div class="st-emotion-cache-1wmy9hl e1f1d6gn1">
                                  <div width="344" data-testid="stVerticalBlock" class="st-emotion-cache-1njjmvq e1f1d6gn2">
                                    <div data-stale="false" width="344" class="element-container st-emotion-cache-lj8h43 e1f1d6gn4" data-testid="element-container">
                                      <div class="row-widget stDownloadButton" data-testid="stDownloadButton" style="width: 344px;">
                                        <button id="downloadButton" kind="secondary" data-testid="baseButton-secondary" class="download-button" style="width: 100%;">
                                          <div data-testid="stMarkdownContainer" class="st-emotion-cache-187vdiz e1nzilvr4">
                                            <p>
                                              <font style="vertical-align: inherit;">
                                                <font style="vertical-align: inherit;">导出{type1}格式</font>
                                              </font>
                                            </p>
                                          </div>
                                        </button>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>

                            <script>
                            var fileBase64 = "{base64}";
                            var fileName = "{os.path.basename(path)}";

                            document.getElementById("downloadButton").addEventListener("click", function() {{
                                var link = document.createElement("a");
                                link.href = "data:application/octet-stream;base64," + fileBase64;
                                link.download = fileName;
                                document.body.appendChild(link);
                                link.click();
                                document.body.removeChild(link);
                            }});
                            </script>
                            """
        return content
