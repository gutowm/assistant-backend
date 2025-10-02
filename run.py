import uvicorn

def start_server():
    uvicorn.run("server:server", host="0.0.0.0", port=8000, reload=True, reload_dirs=["/app"])

if __name__ == "__main__":
    start_server()