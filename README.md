# aid-server
[Client Request]
       ↓
[Router]
   └─ db = Depends(get_db)
       ↓
[Service.signup(db)]
       ↓
[Repository.create_customer(db)]
       ↓
[Repository.create_site(db)]
       ↓
[Service.commit()]
       ↓
[Return Response]