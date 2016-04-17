from apps.moment.models import Moment
all_moments = Moment.objects.all()

MEDIA = '/media/'
PICS = 'pics'
for m in all_moments:
    if PICS in m.content:  # test if have pics
        for index, pic in enumerate(m.content.get(PICS, [])):
            if pic.startswith(MEDIA):
                print('replacing')
                m.content[PICS][index] = pic[len(MEDIA):]
                m.save()

print('replacation end')



