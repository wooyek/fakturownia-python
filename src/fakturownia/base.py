# coding=utf-8


class BaseEndpoint(object):
    def __init__(self, client):
        self.client = client

    def create(self, **kwargs):
        return self.model(self.client, **kwargs).post()

    def __getitem__(self, key):
        return self.model(client=self.client, id=key).get()


class BaseModel(object):
    def __init__(self, client, **kwargs):
        super(BaseModel, self).__setattr__('_client', kwargs.pop('client', client))
        super(BaseModel, self).__setattr__('_data', {'id': None})
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_raw_data(self):
        return self._data

    def post(self, **kwargs):
        data = self.prepare_post_data(**kwargs)
        response = self._client.post(self.get_endpoint(), data)
        self._update_data(response)
        return self

    def put(self, **kwargs):
        data = self.prepare_post_data(**kwargs)
        response = self._client.put(self.get_endpoint(), data)
        self._update_data(response)
        return self

    def prepare_post_data(self, **kwargs):
        data = kwargs or self._data.copy()
        if 'id' in self._data and 'id' not in data:
            data['id'] = self._data['id']
        return {self._data_wrap: data}

    def get(self):
        response = self._client.get(self.get_endpoint())
        self._update_data(response)
        return self

    def delete(self):
        response = self._client.delete(self.get_endpoint())
        return self

    def get_endpoint(self, extra=''):
        if self.id:
            return '{}/{}{}.json'.format(self._endpoint, self.id, extra)
        return self._endpoint + ".json"

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
            msg = '{} instance does not have {} key in data dictionary'
            raise AttributeError(msg.format(self.__class__.__name__, key))
        return self._data[key]

    __getitem__ = __getattr__
