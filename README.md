# ZHANK setup:
### Backend:
1. ```clone``` the repo to your machine and ```cd``` to it,
2. ```pip install -r requirements.txt```
3. ```uvicorn app.main:app --port 80 --reload```


### Frontend:
1. ```clone``` the repo to your machine and ```cd``` to it,
2. ```npm install```
3. ```npm run dev```

---
### Also consider:
- Setting up a virtual environment for python
- All tests are done on the following versions of python: 3.9, 3.13
- You can also spin up containers for both backend and frontend
- Consider setting up frontend container as a service to backend's compose file