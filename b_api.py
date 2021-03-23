from flask_restful import Resource, Api


class SensorData(Resource):
    def get(self, name):
        # for item in items:
        #     if item['name'] == name:
        #         return item
        # or
        item = next(filter(lambda x: x['name'] == name, items), None)
        return {'item': item}, 200 if item else 404

    def post(self, name):
        if next(filter(lambda x: x['name'] == name, items), None):
            return {'message': f'an item with that {name} name already exists'}, 400

        data = request.get_json()
        item = {
            'name': name,
            'price': data['price']
        }
        items.append(item)
        return item, 201