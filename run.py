import uvicorn

def start_server():
    uvicorn.run("server:server", host="localhost", port=8000, reload=True, reload_dirs=["/app"])

if __name__ == "__main__":
    start_server()