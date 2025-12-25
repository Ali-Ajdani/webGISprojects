using System;
using System.Web.Services;

namespace TrianglePerimeterWS
{
    [WebService(Namespace = "http://tempuri.org/")]
    [WebServiceBinding(ConformsTo = WsiProfiles.BasicProfile1_1)]
    public class TriangleService : WebService
    {
        public TriangleService() { }

        // تبدیل درجه به رادیان
        private double DegToRad(double deg)
        {
            return deg * Math.PI / 180.0;
        }

        // محاسبه فاصله بین دو نقطه روی زمین (WGS84)
        private double Distance(double lat1, double lon1, double lat2, double lon2)
        {
            double R = 6378137.0;   // شعاع زمین (متر)

            double dLat = DegToRad(lat2 - lat1);
            double dLon = DegToRad(lon2 - lon1);

            lat1 = DegToRad(lat1);
            lat2 = DegToRad(lat2);

            double a =
                Math.Sin(dLat / 2) * Math.Sin(dLat / 2) +
                Math.Cos(lat1) * Math.Cos(lat2) *
                Math.Sin(dLon / 2) * Math.Sin(dLon / 2);

            double c = 2 * Math.Atan2(Math.Sqrt(a), Math.Sqrt(1 - a));

            return R * c;
        }

        // ⭐ متد سرویس: محاسبه محیط مثلث ⭐
        [WebMethod(Description = "محاسبه محیط مثلث بر اساس مختصات WGS84 (درجه)")]
        public double TrianglePerimeter(
            double Ax, double Ay,
            double Bx, double By,
            double Cx, double Cy)
        {
            double AB = Distance(Ax, Ay, Bx, By);
            double BC = Distance(Bx, By, Cx, Cy);
            double CA = Distance(Cx, Cy, Ax, Ay);

            return AB + BC + CA;
        }
    }
}

