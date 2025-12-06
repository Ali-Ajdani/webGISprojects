using System;
using System.Web.Http;
using WebApplication1.Models;

namespace WebApplication1.Controllers
{
    [RoutePrefix("api/geo")]
    public class GeoController : ApiController
    {
        // GET: api/geo/perimeter?lat1=..&lon1=..&lat2=..&lon2=..&lat3=..&lon3=..
        [HttpGet]
        [Route("perimeter")]
        public double GetPerimeter(
            double lat1, double lon1,
            double lat2, double lon2,
            double lat3, double lon3)
        {
            var A = new GeoPoint { Latitude = lat1, Longitude = lon1 };
            var B = new GeoPoint { Latitude = lat2, Longitude = lon2 };
            var C = new GeoPoint { Latitude = lat3, Longitude = lon3 };

            double AB = Haversine(A, B);
            double BC = Haversine(B, C);
            double CA = Haversine(C, A);

            return AB + BC + CA;
        }

        // متد محاسبه فاصله بین دو نقطه (فرمول هاورساین)
        private double Haversine(GeoPoint p1, GeoPoint p2)
        {
            const double R = 6371000; // شعاع زمین (متر)

            double lat1 = Degrees(p1.Latitude);
            double lat2 = Degrees(p2.Latitude);
            double dLat = Degrees(p2.Latitude - p1.Latitude);
            double dLon = Degrees(p2.Longitude - p1.Longitude);

            double a =
                Math.Sin(dLat / 2) * Math.Sin(dLat / 2) +
                Math.Cos(lat1) * Math.Cos(lat2) *
                Math.Sin(dLon / 2) * Math.Sin(dLon / 2);

            double c = 2 * Math.Atan2(Math.Sqrt(a), Math.Sqrt(1 - a));

            return R * c; // Distance in meters
        }

        // تبدیل درجه به رادیان
        private double Degrees(double deg)
        {
            return deg * Math.PI / 180;
        }
    }
}
