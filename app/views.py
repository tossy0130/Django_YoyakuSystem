from calendar import calendar
from email.policy import default
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from pytz import timezone

from app.models import Store, Staff, Booking
from django.views.generic import View
from django.shortcuts import render

from datetime import datetime, date, timedelta, time
from django.db.models import Q
from django.utils.timezone import localtime, make_aware

from app.forms import BookingForm

# Create your views here.


# === 予約　フォーム処理
class BookingView(View):
    def get(self, request, *args, **kwargs):
        staff_data = Staff.objects.filter(
            id=self.kwargs['pk']).select_related('user').select_related('store')[0]
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
        staff_data = get_object_or_404(Staff, id=self.kwargs['pk'])
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        hour = self.kwargs.get('hour')
        start_time = make_aware(
            datetime(year=year, month=month, day=day, hour=hour))
        end_time = make_aware(
            datetime(year=year, month=month, day=day, hour=hour + 1))
        booking_data = Booking.objects.filter(
            staff=staff_data, start=start_time)
        form = BookingForm(request.POST or None)
        if booking_data.exists():
            form.add_error(None, '既に予約があります。\別の日時でお願いします。')
        else:
            if form.is_valid():
                booking = Booking()
                booking.staff = staff_data
                booking.start = start_time
                booking.end = end_time
                # form.cleaned_data => バリデートされた後のデータが入る
                booking.first_name = form.cleaned_data['first_name']
                booking.last_name = form.cleaned_data['last_name']
                booking.tel = form.cleaned_data['tel']
                booking.remarks = form.cleaned_data['remarks']
                booking.save()
                return redirect('store')

        return render(request, 'app/booking.html', {
            'staff_data': staff_data,
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'form': form,
        })

# 予約処理
# 日付と時間で 2 次元配列を使用


class CalendarView(View):
    def get(self, request, *args, **kwargs):
        staff_data = Staff.objects.filter(id=self.kwargs['pk']).select_related(
            'user').select_related('store')[0]
        today = date.today()
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
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
        # 10時～20時
        for hour in range(10, 21):
            row = {}
            # 日付を出力
            for day in days:
                row[day] = True
            calendar[hour] = row
        start_time = make_aware(datetime.combine(
            start_day, time(hour=10, minute=0, second=0)))
        end_time = make_aware(datetime.combine(
            end_day, time(hour=20, minute=0, second=0)))
        booking_data = Booking.objects.filter(staff=staff_data).exclude(
            Q(start__gt=end_time) | Q(end__lt=start_time))
        for booking in booking_data:
            local_time = localtime(booking.start)
            booking_date = local_time.date()
            booking_hour = local_time.hour
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


# スタッフ一覧
class StaffView(View):
    def get(self, request, *args, **kwargs):
        # get_object_or_404関数を使用することで、店舗データがひとつもない場合に、404 エラーを返してくれる。
        # self.kwargs['pk']で URL の店舗 ID を取得
        store_data = get_object_or_404(Store, id=self.kwargs['pk'])
        staff_data = Staff.objects.filter(
            store=store_data).select_related('user')

        return render(request, 'app/staff.html', {
            'store_data': store_data,
            'staff_data': staff_data,
        })


class StoreView(View):
    def get(self, request, *args, **kwargs):
        store_data = Store.objects.all()  # Store テーブル　値　全件取得

        return render(request, 'app/store.html', {
            'store_data': store_data,
        })


class IndexView(LoginRequiredMixin, TemplateView):
    # LoginRequiredMixinクラスを継承させることによって、
    # ログインしていない状態でアクセスした場合にリダイレクトするように設定できる。
    template_name = "app/index.html"
    login_url = '/accounts/login/'
