using SampleProductApi.Models;

namespace SampleProductApi.Services;

public interface IProductService
{
    Task<IReadOnlyCollection<Product>> GetProductsAsync();

    Task<Product?> GetProductByIdAsync(int id);
}