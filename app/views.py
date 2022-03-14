from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Store, Staff, Booking
from django.views.generic import View
from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime, date, timedelta, time
from django.db.models import Q
from django.utils.timezone import localtime, make_aware
from app.forms import BookingForm
from django.views.decorators.http import require_POST


#LoginRequiredMixinを継承
class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "app/index.html"
    #login_url変数にログイン画面の URL を指定すると、リダイレクトする
    login_url = '/accounts/login/'

class StoreView(View):
    def get(self, request, *args, **kwargs):
        #request.user.is_authenticatedでログイン状態。
        if request.user.is_authenticated:
            start_date = date.today()
            weekday = start_date.weekday()
            
            # カレンダー日曜日開始
            if weekday != 6:
                start_date = start_date - timedelta(days=weekday + 1)
            #もしログインしたら、マイページに画面遷移。
            return redirect('mypage', start_date.year, start_date.month, start_date.day)
        
        #.all()を使ってすべてのデータを取得
        store_data = Store.objects.all()

        #店舗一覧に画面遷移。
        return render(request, 'app/store.html', {
            'store_data': store_data,
        })

class StaffView(View):
    def get(self, request, *args, **kwargs):
        #get_object_or_404関数を使用することで、店舗データがひとつもない場合に、404 エラーを返す。
        #self.kwargs['pk']で URL の店舗 ID を取得。
        store_data = get_object_or_404(Store, id=self.kwargs['pk'])
        staff_data = Staff.objects.filter(store=store_data).select_related('user')

        return render(request, 'app/staff.html', {
            'store_data': store_data,
            'staff_data': staff_data,
        })

class CalendarView(View):
    def get(self, request, *args, **kwargs):
        #select_relatedを使用することで、SQL を実行する回数を減らすことができる。
        #スタッフモデルからユーザー情報や店舗情報を取得するときに、select_relatedを使用することによって、SQL の実行を一度にしている。
        staff_data = Staff.objects.filter(id=self.kwargs['pk']).select_related('user').select_related('store')[0]
        today = date.today()
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        #もし URL に year、month、day がある場合は、その日をカレンダーの始めの日
        if year and month and day:
            # 週始め
            start_date = date(year=year, month=month, day=day)
        else:
            start_date = today
        # 1週間
        days = [start_date + timedelta(days=day) for day in range(7)]
        start_day = days[0]
        end_day = days[-1]

        calendar = {}
        # 10時～20時 （店の営業時間）
        for hour in range(10, 21):
            row = {}
            for day in days:
                #予約前の変数はTrue
                #予約されたらこの変数をFalseに変更
                row[day] = True
            calendar[hour] = row
            #combineを使用することによって、日付けと時間を合わせる
            #make_aware関数を使用することによって、設定したでタイムゾーンに変更。
            #native time はタイムゾーンを意識しない時間
            #aware time はタイムゾーンを意識した時間
        start_time = make_aware(datetime.combine(start_day, time(hour=10, minute=0, second=0)))
        end_time = make_aware(datetime.combine(end_day, time(hour=20, minute=0, second=0)))
        # Q オブジェクトを使用することによって、OR 検索する。
        # __gt：より大きい
        # __gte：以上
        # __lt：より小さい
        # __lte：以下
        booking_data = Booking.objects.filter(staff=staff_data).exclude(Q(start__gt=end_time) | Q(end__lt=start_time))
        for booking in booking_data:
            #localtime 関数を使用することによって、現地のタイムゾーンに変更。
            local_time = localtime(booking.start)
            booking_date = local_time.date()
            booking_hour = local_time.hour
            #予約がある場合は、変数をFalseに変更。
            if (booking_hour in calendar) and (booking_date in calendar[booking_hour]):
                calendar[booking_hour][booking_date] = False

        return render(request, 'app/calendar.html', {
            'staff_data': staff_data,
            'calendar': calendar,
            'days': days,
            'start_day': start_day,
            'end_day': end_day,
            'before': days[0] - timedelta(days=7),
            'next': days[-1] + timedelta(days=1),
            'today': today,
        })

class BookingView(View):
    def get(self, request, *args, **kwargs):
        #URL の店舗 ID でフィルターをかけて、それをstaff_dataに入れる。
        #select_relatedを使用することによって、SQL の実行を一度にしている。
        staff_data = Staff.objects.filter(id=self.kwargs['pk']).select_related('user').select_related('store')[0]

        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        hour = self.kwargs.get('hour')
        form = BookingForm(request.POST or None)

        return render(request, 'app/booking.html', {
            'staff_data': staff_data,
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        #get_object_or_404関数を使用することで、店舗データがひとつもない場合に、404 エラーを返す。
        staff_data = get_object_or_404(Staff, id=self.kwargs['pk'])
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        hour = self.kwargs.get('hour')
        start_time = make_aware(datetime(year=year, month=month, day=day, hour=hour))
        end_time = make_aware(datetime(year=year, month=month, day=day, hour=hour + 1))
        #予約情報にスタッフと時間でフィルターして、データが存在していたら、警告だす
        booking_data = Booking.objects.filter(staff=staff_data, start=start_time)
        form = BookingForm(request.POST or None)
        if booking_data.exists():
            form.add_error(None, '既に予約があります。\n別の日時で予約をお願いします。')
        else:
            #予約確定ボタンを押したら、ユーザーデータをデーターベースに保存
            if form.is_valid():
                booking = Booking()
                booking.staff = staff_data
                booking.start = start_time
                booking.end = end_time
                booking.first_name = form.cleaned_data['first_name']
                booking.last_name = form.cleaned_data['last_name']
                booking.tel = form.cleaned_data['tel']
                booking.remarks = form.cleaned_data['remarks']
                booking.save()
                #thanks.htmlに画面遷移
                return redirect('thanks') 

        return render(request, 'app/booking.html', {
            'staff_data': staff_data,
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'form': form,
        })

class ThanksView(TemplateView):
    template_name = 'app/thanks.html'

class MyPageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        staff_data = Staff.objects.filter(id=request.user.id).select_related('user').select_related('store')[0]
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        start_date = date(year=year, month=month, day=day)
        days = [start_date + timedelta(days=day) for day in range(7)]
        start_day = days[0]
        end_day = days[-1]

        calendar = {}
        # 10時～20時
        for hour in range(10, 21):
            row = {}
            for day_ in days:
                row[day_] = ""
            calendar[hour] = row
        start_time = make_aware(datetime.combine(start_day, time(hour=10, minute=0, second=0)))
        end_time = make_aware(datetime.combine(end_day, time(hour=20, minute=0, second=0)))
        booking_data = Booking.objects.filter(staff=staff_data).exclude(Q(start__gt=end_time) | Q(end__lt=start_time))
        for booking in booking_data:
            local_time = localtime(booking.start)
            booking_date = local_time.date()
            booking_hour = local_time.hour
            #予約した人の名前を calendar 変数に設定
            #カレンダーで名前を表示
            if (booking_hour in calendar) and (booking_date in calendar[booking_hour]):
                calendar[booking_hour][booking_date] = booking.first_name

        return render(request, 'app/mypage.html', {
            'staff_data': staff_data,
            'booking_data': booking_data,
            'calendar': calendar,
            'days': days,
            'start_day': start_day,
            'end_day': end_day,
            'before': days[0] - timedelta(days=7),
            'next': days[-1] + timedelta(days=1),
            'year': year,
            'month': month,
            'day': day,
        })

#@require_POST→ボタンをクリックしたときにのみ動作
@require_POST
def Holiday(request, year, month, day, hour):
    staff_data = Staff.objects.get(id=request.user.id)
    start_time = make_aware(datetime(year=year, month=month, day=day, hour=hour))
    end_time = make_aware(datetime(year=year, month=month, day=day, hour=hour + 1))

    # 休日追加
    Booking.objects.create(
        staff=staff_data,
        start=start_time,
        end=end_time,
    )

    start_date = date(year=year, month=month, day=day)
    weekday = start_date.weekday()
    # カレンダー日曜日開始
    if weekday != 6:
        start_date = start_date - timedelta(days=weekday + 1)
    return redirect('mypage', year=start_date.year, month=start_date.month, day=start_date.day)

#@require_POST→ボタンをクリックしたときにのみ動作
@require_POST
def Delete(request, year, month, day, hour):
    start_time = make_aware(datetime(year=year, month=month, day=day, hour=hour))
    booking_data = Booking.objects.filter(start=start_time)

    # 予約削除
    booking_data.delete()

    start_date = date(year=year, month=month, day=day)
    weekday = start_date.weekday()
    # カレンダー日曜日開始
    if weekday != 6:
        start_date = start_date - timedelta(days=weekday + 1)
    return redirect('mypage', year=start_date.year, month=start_date.month, day=start_date.day)
