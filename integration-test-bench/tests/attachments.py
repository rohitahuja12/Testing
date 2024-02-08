import unittest
import asyncio
import io
import sys
sys.path.insert(0, './common')
import dbclient

class TestAttachments(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(self):

        res = asyncio.run(dbclient.create('scans', {
            'readerSerialNumber': '0',
            'name': 'anyscan',
            'productId': '',
            'protocol': 'pArray',
            'status': 'COMPLETE'
        }))
        self.scanId = res['_id']
        self.attachmentName = 'testAttachment'

    @classmethod
    def tearDownClass(self):
        res = asyncio.run(dbclient.delete('scans', self.scanId))

    async def test_create_and_delete_attachment(self):
        buff = io.BytesIO(b'this is my data')
        res = await dbclient.createAttachment('scans', self.scanId, buff, self.attachmentName)
        assert res

        res = await dbclient.deleteAttachment('scans', self.scanId, self.attachmentName)
        assert res

        try:
            await dbclient.getAttachment('scans', self.scanId, self.attachmentName)
        except Exception as e:
            return 
        raise Exception('attachment not deleted')


    async def test_get_attachment(self):
        data = b'this is my data'
        buff = io.BytesIO(data)
        res = await dbclient.createAttachment('scans', self.scanId, buff, self.attachmentName)
        res = await dbclient.getAttachment('scans', self.scanId, self.attachmentName)
        assert res == data

    async def test_get_all_attachments(self):
        name1 = self.attachmentName + "1"
        name2 = self.attachmentName + "2"
        data1 = b'this is my first data'
        data2 = b'this is my second data'
        buff1 = io.BytesIO(data1)
        buff2 = io.BytesIO(data2)
        res = await dbclient.createAttachment('scans', self.scanId, buff1, name1)
        res = await dbclient.createAttachment('scans', self.scanId, buff2, name2)

        res = await dbclient.getAllAttachments('scans', self.scanId)
        print(f'geta lla attachments restuls: {res}')
        assert name1 in [f['filename'] for f in res]
        assert name2 in [f['filename'] for f in res]


if __name__ == "__main__":
    unittest.main()
