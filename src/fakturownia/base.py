# coding=utf-8

class BaseEndpoint(object):
    def __init__(self, client):
        self.client = client
    #
    # def post(self, ):
    #     self.client.post(self.endpoint)

    # def create(self, **kwargs):


class BaseModel(object):
    def __init__(self, client, **kwargs):
        super(BaseModel, self).__setattr__('_client', kwargs.pop('client', client))
        super(BaseModel, self).__setattr__('_data', {'id': None})
        for k, v in kwargs.items():
            setattr(self, k, v)

    def post(self):
        data = self.prepare_post_data()
        response = self._client.post(self.get_endpoint(), data)
        self._update_data(response)
        return self

    def prepare_post_data(self):
        data = self._data.copy()
        # if data['id'] is None:
        #     data.pop('id')
        return {self.data_wrap: data}

    def get(self):
        response = self._client.get(self.get_endpoint())
        self._update_data(response)
        return self

    def get_endpoint(self, extra=''):
        if self.id:
            return '{}/{}{}.json'.format(self.endpoint, self.id, extra)
        return self.endpoint + ".json"

    def _update_data(self, data):
        new_id = data.get('id', None)
        if self.id and new_id:
            assert self.id == new_id, 'Existing id does not match update data {}!={}'.format(self.id, new_id)
        self._data.update(data)

    def __setattr__(self, name, value):
        if name in self.__dict__.keys() or name in self.__class__.__dict__.keys():
            return super(BaseModel, self).__setattr__(name, value)
        self._data[name] = value

    def __getattr__(self, key):
        if key not in self._data:
            raise AttributeError
        return self._data[key]

    __getitem__ = __getattr__
