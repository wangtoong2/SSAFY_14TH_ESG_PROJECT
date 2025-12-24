## 2025.12.16
- DEFAULT_AUTO_FIELD error occured
    ```python
    # to resolve error code added to back/ESG/settings.py
    DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
## pinia에 저장된 token이 local storage에 반영되지 않는 문제가 발생
- main.js에 작성 필수
    ```
    import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
    pinia.use(piniaPluginPersistedstate)
    ```