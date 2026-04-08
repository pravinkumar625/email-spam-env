from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Server is running"}


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()