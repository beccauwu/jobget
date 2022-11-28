import jobget
import nose

class TestJobget:
    def test_get(self):
        client = jobget.Client()
        client.exec()
        #should raise error since no params
        assert client.status.code == 3
