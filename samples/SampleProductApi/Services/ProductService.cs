using SampleProductApi.Models;

namespace SampleProductApi.Services;

public class ProductService : IProductService
{
    private static readonly IReadOnlyCollection<Product> Products =
    [
        new Product
        {
            Id = 1,
            Name = "Laptop",
            Price = 1200
        },
        new Product
        {
            Id = 2,
            Name = "Keyboard",
            Price = 120
        },
        new Product
        {
            Id = 3,
            Name = "Monitor",
            Price = 450
        }
    ];

    public Task<IReadOnlyCollection<Product>> GetProductsAsync()
    {
        return Task.FromResult(Products);
    }

    public Task<Product?> GetProductByIdAsync(int id)
    {
        var product = Products.FirstOrDefault(
            product => product.Id == id
        );

        return Task.FromResult(product);
    }
}