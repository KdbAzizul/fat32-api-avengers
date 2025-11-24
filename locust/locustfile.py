from locust import HttpUser, task, between

class MyUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        self.client.verify = False

    @task
    def my_test(self):
        self.client.get("/api/v1/campaign-service/campaigns")
