using System;
using System.Web.Http;
using AuthProject.Models;

namespace AuthProject.Controllers
{
    [RoutePrefix("api/auth")]
    public class AuthController : ApiController
    {
        [HttpPost]
        [Route("login")]
        public IHttpActionResult Login(LoginRequest request)
        {
            if (request == null)
                return BadRequest();

            var token = Guid.NewGuid().ToString();

            TokenStore.Tokens[token] = true;

            return Ok(new { token });
        }

        [HttpGet]
        [Route("data")]
        public IHttpActionResult GetSecureData()
        {
            var auth = Request.Headers.Authorization;

            if (auth == null || auth.Scheme != "Bearer")
                return Unauthorized();

            var token = auth.Parameter;

            if (string.IsNullOrEmpty(token))
                return Unauthorized();

            if (!TokenStore.Tokens.ContainsKey(token))
                return Unauthorized();

            return Ok(new { message = "OK - Token is valid" });
        }
    }
}
