import struct
import cocos
from cocos.sprite import Sprite
from pyaudio import PyAudio, paInt16
from ppx import PPX
from block import Block
# TODO: 把图片某一目录下进行引用，对文件操作不熟练


class VoiceGame(cocos.layer.ColorLayer):
    is_event_handler = True

    def __init__(self):
        super(VoiceGame, self).__init__(255, 255, 255, 255, 800, 600)

        # 右上角的标志
        self.logo = Sprite('ppx.png')
        self.logo.position = 550, 400
        self.add(self.logo, 9999)

        # init voice
        # pyAudion内部缓存的块的大小
        self.NUM_SAMPLES = 1000
        # 声音保存的阈值
        self.LEVEL = 1500

        # 左上角的声音条
        self.voicebar = Sprite('black.png', color=(0, 0, 255))
        self.voicebar.position = 20, 450
        self.voicebar.scale_y = 0.1
        self.voicebar.img_anchor = 0, 0
        self.add(self.voicebar)

        self.ppx = PPX()
        self.add(self.ppx)

        self.floor = cocos.cocosnode.CocosNode()
        self.add(self.floor)
        pos = 0, 100
        for i in range(100):
            b = Block(pos)
            self.floor.add(b)
            pos = b.x + b.width, b.height

        # 开启声音输入
        pa = PyAudio()
        SAMPLING_RATE = int(pa.get_device_info_by_index(0)['defaultSampleRate'])
        self.stream = pa.open(format=paInt16, channels=1,
                              rate=SAMPLING_RATE, input=True, frames_per_buffer=self.NUM_SAMPLES)
        self.schedule(self.update)

    def collide(self):
        px = self.ppx.x - self.floor.x
        for b in self.floor.get_children():
            if b.x <= px + self.ppx.width * 0.8 and px + self.ppx.width * 0.2 <= b.x + b.width:
                if self.ppx.y < b.height:
                    self.ppx.land(b.height)
                    break

    def update(self, dt):
        # 读入NUM_SAMPLES个取样

        string_audio_data = self.stream.read(self.NUM_SAMPLES)
        k = max(struct.unpack('1000h', string_audio_data))
        # print k
        self.voicebar.scale_x = k / 10000.0
        if k > 3000:
            # 通过小黑块的后移实现皮皮虾的前进
            self.floor.x -= min((k / 20.0), 150) * dt
            if k > 8000:
                self.ppx.jump((k - 8000) / 1000.0)
        self.collide()

    def reset(self):
        self.floor.x = 0

cocos.director.director.init(caption="Let's GO! PiPiXia!")
cocos.director.director.run(cocos.scene.Scene(VoiceGame()))
