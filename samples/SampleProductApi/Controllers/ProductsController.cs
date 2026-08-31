using Microsoft.AspNetCore.Mvc;
using SampleProductApi.Models;
using SampleProductApi.Services;

namespace SampleProductApi.Controllers;

[ApiController]
[Route("api/products")]
public class ProductsController : ControllerBase
{
    private readonly IProductService _productService;

    public ProductsController(
        IProductService productService)
    {
        _productService = productService;
    }

    [HttpGet]
    public async Task<ActionResult<IReadOnlyCollection<Product>>>
        GetProducts()
    {
        var products =
            await _productService.GetProductsAsync();

        return Ok(products);
    }

    [HttpGet("{id:int}")]
    public async Task<ActionResult<Product>>
        GetProductById(int id)
    {
        var product =
            await _productService.GetProductByIdAsync(id);

        if (product is null)
        {
            return NotFound();
        }

        return Ok(product);
    }
}